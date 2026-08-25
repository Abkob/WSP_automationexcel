from __future__ import annotations

import re
import json
from pathlib import Path
from typing import Sequence

import numpy as np

from config import AppSettings
from database.db import create_session_factory, create_sqlite_engine, initialize_database
from database.models import SemanticEmbedding, StudentCurrent
from services.filter_service import BooleanFilter, FilterRequest, SemanticFilter, execute_filter_request
from services.semantic_document_service import build_student_semantic_profiles
from services.semantic_search_service import (
    build_ollama_rag_prompt,
    compact_rag_profile_text,
    normalize_rag_match_scores,
    rank_student_rows_by_ollama_rag,
    rank_student_rows_by_vector_search,
    retrieve_rag_candidate_profiles,
    sync_student_semantic_index,
)
from services.semantic_service import SemanticMatch
from services.vector_store_service import FaissVectorStore


class MeaningEmbeddingModel:
    model_name = "fake-meaning-model"

    def __init__(self) -> None:
        self.document_encode_calls = 0
        self.query_encode_calls = 0

    def encode(self, texts: Sequence[str], *, kind: str) -> np.ndarray:
        if kind == "document":
            self.document_encode_calls += len(texts)
        else:
            self.query_encode_calls += len(texts)
        return np.array([meaning_vector(text) for text in texts], dtype=np.float32)


class BrokenEmbeddingModel:
    model_name = "broken-model"

    def encode(self, texts: Sequence[str], *, kind: str) -> np.ndarray:
        raise RuntimeError("embedding model unavailable")


def meaning_vector(text: str) -> list[float]:
    clean_text = text.casefold()
    tokens = set(re.findall(r"[a-z]+", clean_text))
    admin_terms = {"boring", "repetitive", "file", "files", "office", "record", "records", "form", "forms", "document", "cleanup", "careful"}
    lab_terms = {"lab", "laboratory", "sample", "microscope"}
    if tokens & admin_terms:
        return [1.0, 0.0, 0.0]
    if tokens & lab_terms:
        return [0.0, 1.0, 0.0]
    return [0.0, 0.0, 1.0]


def make_settings(tmp_path: Path) -> AppSettings:
    return AppSettings(data_dir=tmp_path / "data", runtime_mode="testing")


def make_session_factory(tmp_path: Path):
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    return create_session_factory(engine)


def test_semantic_index_sync_embeds_only_new_or_changed_profiles(tmp_path: Path) -> None:
    settings = make_settings(tmp_path)
    session_factory = make_session_factory(tmp_path)
    model = MeaningEmbeddingModel()
    store = FaissVectorStore(settings.semantic_index_dir)

    with session_factory() as session:
        session.add_all(
            [
                StudentCurrent(STUD_ID="1001", WSP_TECHNICAL_SKILLS="document cleanup and careful record checks"),
                StudentCurrent(STUD_ID="1002", WSP_TECHNICAL_SKILLS="lab sample labels"),
            ]
        )
        session.commit()
        students = tuple(session.query(StudentCurrent).order_by(StudentCurrent.STUD_ID).all())

        first = sync_student_semantic_index(session, settings, students, embedding_model=model, vector_store=store)
        second = sync_student_semantic_index(session, settings, students, embedding_model=model, vector_store=store)
        students[0].WSP_TECHNICAL_SKILLS = "document cleanup and careful record checks with spreadsheets"
        session.commit()
        third = sync_student_semantic_index(session, settings, students, embedding_model=model, vector_store=store)

        assert first.embedded_count == 2
        assert second.embedded_count == 0
        assert second.skipped_count == 2
        assert third.embedded_count == 1
        assert model.document_encode_calls == 3
        assert session.query(SemanticEmbedding).count() == 2


def test_semantic_index_sync_prunes_students_outside_active_dataset(tmp_path: Path) -> None:
    settings = make_settings(tmp_path)
    session_factory = make_session_factory(tmp_path)
    model = MeaningEmbeddingModel()
    store = FaissVectorStore(settings.semantic_index_dir)

    with session_factory() as session:
        active = StudentCurrent(STUD_ID="1001", WSP_TECHNICAL_SKILLS="document cleanup")
        inactive = StudentCurrent(
            STUD_ID="1002",
            WSP_TECHNICAL_SKILLS="lab sample labels",
            missing_from_latest_import=True,
        )
        session.add_all((active, inactive))
        session.commit()
        sync_student_semantic_index(session, settings, (active, inactive), embedding_model=model, vector_store=store)
        session.commit()

        result = sync_student_semantic_index(
            session,
            settings,
            (active,),
            embedding_model=model,
            vector_store=store,
            prune_stale=True,
        )
        session.commit()

        assert result.embedded_count == 0
        assert store.record_ids() == {"1001"}
        assert {row.STUD_ID for row in session.query(SemanticEmbedding).all()} == {"1001"}


def test_vector_search_retrieves_vague_related_profile_without_exact_keyword_overlap(tmp_path: Path) -> None:
    settings = make_settings(tmp_path)
    session_factory = make_session_factory(tmp_path)
    model = MeaningEmbeddingModel()
    store = FaissVectorStore(settings.semantic_index_dir)

    with session_factory() as session:
        session.add_all(
            [
                StudentCurrent(
                    STUD_ID="1001",
                    STUD_NAME="Admin Fit",
                    WSP_ORGANIZATIONAL_SKILLS="Careful record organization and document checking",
                    WSP_PREFERRED_TYPE_OF_WORK="Forms review and import cleanup",
                ),
                StudentCurrent(
                    STUD_ID="1002",
                    STUD_NAME="Lab Fit",
                    WSP_PREFERRED_TYPE_OF_WORK="Laboratory sample preparation",
                ),
            ]
        )
        session.commit()
        candidates = tuple(session.query(StudentCurrent).order_by(StudentCurrent.STUD_ID).all())

        matches = rank_student_rows_by_vector_search(
            settings,
            session,
            SemanticFilter("I need someone for boring repetitive office work who will not mess up files", minimum_score=0.0),
            candidates,
            embedding_model=model,
            vector_store=store,
        )

    assert [match.STUD_ID for match in matches] == ["1001", "1002"]
    assert matches[0].score > matches[1].score
    assert "Embedding match" in matches[0].reason
    assert "Closest original evidence" in matches[0].reason
    assert "Forms review and import cleanup" in matches[0].reason
    assert "Organizational skills" in matches[0].reason


def test_structured_filters_are_applied_before_vector_search(tmp_path: Path) -> None:
    settings = make_settings(tmp_path)
    session_factory = make_session_factory(tmp_path)
    model = MeaningEmbeddingModel()
    store = FaissVectorStore(settings.semantic_index_dir)

    with session_factory() as session:
        session.add_all(
            [
                StudentCurrent(STUD_ID="1001", PROBATION=True, WSP_PREFERRED_TYPE_OF_WORK="document cleanup"),
                StudentCurrent(STUD_ID="1002", PROBATION=False, WSP_PREFERRED_TYPE_OF_WORK="document cleanup"),
            ]
        )
        session.commit()
        result = execute_filter_request(
            session,
            FilterRequest(
                boolean_filters=(BooleanFilter("PROBATION", False),),
                semantic_filter=SemanticFilter("careful file work", minimum_score=0.0),
            ),
            semantic_ranker=lambda semantic_filter, rows: rank_student_rows_by_vector_search(
                settings,
                session,
                semantic_filter,
                rows,
                embedding_model=model,
                vector_store=store,
            ),
        )

    assert [student.STUD_ID for student in result.rows] == ["1002"]


def test_qwen_or_embedding_unavailable_falls_back_to_text_match(tmp_path: Path) -> None:
    settings = make_settings(tmp_path)
    session_factory = make_session_factory(tmp_path)

    with session_factory() as session:
        session.add(
            StudentCurrent(
                STUD_ID="1001",
                WSP_TECHNICAL_SKILLS="Excel spreadsheet reporting",
                WSP_PREFERRED_TYPE_OF_WORK="Data entry",
            )
        )
        session.commit()
        candidates = tuple(session.query(StudentCurrent).all())

        matches = rank_student_rows_by_vector_search(
            settings,
            session,
            SemanticFilter("spreadsheet reporting", minimum_score=0.0),
            candidates,
            embedding_model=BrokenEmbeddingModel(),
            vector_store=FaissVectorStore(settings.semantic_index_dir),
        )

    assert [match.STUD_ID for match in matches] == ["1001"]
    assert "Text match fallback" in matches[0].reason
    assert "embedding search was unavailable" in matches[0].reason


def test_ollama_rag_ranker_sends_retrieved_profiles_to_local_model(tmp_path: Path) -> None:
    settings = make_settings(tmp_path)
    session_factory = make_session_factory(tmp_path)

    with session_factory() as session:
        session.add_all(
            [
                StudentCurrent(
                    STUD_ID="1001",
                    MAJR_DESC="Graphic Design",
                    CUM_GPA=3.2,
                    WSP_TECHNICAL_SKILLS="Canva, poster layouts, social media scheduling",
                    WSP_PREFERRED_TYPE_OF_WORK="Design and communications work",
                ),
                StudentCurrent(
                    STUD_ID="1002",
                    MAJR_DESC="Biology",
                    CUM_GPA=3.8,
                    WSP_TECHNICAL_SKILLS="Lab sample logs",
                    WSP_PREFERRED_TYPE_OF_WORK="Laboratory assistant",
                ),
            ]
        )
        session.commit()
        candidates = tuple(session.query(StudentCurrent).order_by(StudentCurrent.STUD_ID).all())

        def fake_chat(prompt: str, system_prompt: str | None) -> str:
            payload = json.loads(prompt)
            assert "offline student matching assistant" in (system_prompt or "")
            assert payload["request"] == "social media poster design"
            assert [candidate["STUD_ID"] for candidate in payload["candidates"]] == ["1001", "1002"]
            assert "student@example" not in prompt
            return json.dumps(
                {
                    "matches": [
                        {
                            "STUD_ID": "1001",
                            "score": 0.93,
                            "reason": "Canva, poster layouts, and social media scheduling match the design request.",
                        },
                        {
                            "STUD_ID": "1002",
                            "score": 0.18,
                            "reason": "Lab work is not a strong fit for design communications.",
                        },
                    ]
                }
            )

        matches = rank_student_rows_by_ollama_rag(
            settings,
            session,
            SemanticFilter("social media poster design", minimum_score=0.1),
            candidates,
            chat_runner=fake_chat,
        )

    assert [match.STUD_ID for match in matches] == ["1001", "1002"]
    assert matches[0].score == 0.93
    assert "Canva" in matches[0].reason
    assert "fallback" not in matches[0].reason.casefold()


def test_ollama_rag_retrieval_limits_candidates_before_model_prompt() -> None:
    profiles = build_student_semantic_profiles(
        [
            StudentCurrent(STUD_ID="1001", WSP_TECHNICAL_SKILLS="Canva posters social media"),
            StudentCurrent(STUD_ID="1002", WSP_TECHNICAL_SKILLS="Excel spreadsheet reporting"),
            StudentCurrent(STUD_ID="1003", WSP_TECHNICAL_SKILLS="Lab sample logs"),
        ]
    )

    retrieved = retrieve_rag_candidate_profiles("poster design", profiles, candidate_limit=2)
    prompt = build_ollama_rag_prompt("poster design", retrieved, top_k=2, profile_text_limit=120)
    payload = json.loads(prompt)

    assert len(payload["candidates"]) == 2
    assert payload["candidates"][0]["STUD_ID"] == "1001"


def test_compact_rag_profile_prioritizes_matching_fields() -> None:
    profile = build_student_semantic_profiles(
        [
            StudentCurrent(
                STUD_ID="1001",
                MAJR_DESC="Graphic Design",
                CLAS_DESC="Sophomore",
                CUM_GPA=3.2,
                PROBATION=False,
                WSP_TECHNICAL_SKILLS="Canva, poster layouts, social media scheduling",
                WSP_PREFERRED_TYPE_OF_WORK="Design and communications work",
            )
        ]
    )[0]

    text = compact_rag_profile_text(profile, max_length=180)

    assert "Major: Graphic Design" in text
    assert "Skills: Canva" in text
    assert "Preferred: Design" in text
    assert "Student profile for work-study matching" not in text


def test_qwen_zero_scores_are_repaired_from_rank_order() -> None:
    matches = normalize_rag_match_scores(
        (
            SemanticMatch("1001", 0.0, "Strong design match"),
            SemanticMatch("1002", 0.0, "Weaker design match"),
        )
    )

    assert matches[0].score == 0.9
    assert matches[1].score == 0.8
    assert "Qwen ranking order" in matches[0].reason
