from __future__ import annotations

import collections
import json
from dataclasses import dataclass
from typing import Iterable

import numpy as np
from sqlalchemy.orm import Session

from config import AppSettings
from database.models import SemanticEmbedding, StudentCurrent
from services.chat_orchestrator import interpret_chat_search_request
from services.embedding_service import EmbeddingModel, get_default_embedding_model
from services.explanation_service import build_local_semantic_explanation
from services.filter_service import SemanticFilter
from services.semantic_document_service import (
    SEMANTIC_PROFILE_SOURCE_COLUMN,
    StudentSemanticProfile,
    build_student_semantic_profiles,
)
from services.semantic_service import (
    SemanticCandidate,
    SemanticChatRunner,
    SemanticMatch,
    clean_semantic_value,
    parse_semantic_match_response,
    rank_semantic_candidates_locally,
    rank_student_rows_semantically,
    run_ollama_chat,
    truncate_semantic_prompt_text,
)
from services.vector_store_service import DEFAULT_VECTOR_STORE_NAME, FaissVectorStore, VectorRecord


# ── index freshness tracking ──────────────────────────────────────────────────
# When the background reindex finishes after an import it calls mark_index_fresh().
# rank_student_rows_by_vector_search skips the per-search sync while the index
# is fresh, cutting 300-500ms overhead on repeated searches.
# Any new import calls mark_index_stale() first so the next search re-syncs.
import threading as _threading
_index_fresh   = False
_reindex_running = False
_index_lock    = _threading.Lock()

def mark_index_fresh() -> None:
    global _index_fresh, _reindex_running
    with _index_lock:
        _index_fresh     = True
        _reindex_running = False

def mark_index_stale() -> None:
    global _index_fresh
    with _index_lock:
        _index_fresh = False

def mark_reindex_started() -> None:
    global _reindex_running
    with _index_lock:
        _reindex_running = True

def _is_index_fresh() -> bool:
    """True when the background reindex finished and no import has arrived since."""
    with _index_lock:
        return _index_fresh

def _reindex_in_progress() -> bool:
    """True while the background thread is actively encoding profiles."""
    with _index_lock:
        return _reindex_running


# ── query vector LRU cache ────────────────────────────────────────────────────
# Avoids re-encoding the same query string on repeated searches.
# Key: (model_name, query_text) → value: encoded vector as tuple (hashable).
_QUERY_VECTOR_CACHE: collections.OrderedDict[tuple[str, str], tuple[float, ...]] = collections.OrderedDict()
_QUERY_VECTOR_CACHE_LOCK = _threading.Lock()
_QUERY_VECTOR_CACHE_MAX = 64


def _get_query_vector(model: EmbeddingModel, query: str) -> np.ndarray:
    cache_key = (model.model_name, query)
    with _QUERY_VECTOR_CACHE_LOCK:
        if cache_key in _QUERY_VECTOR_CACHE:
            _QUERY_VECTOR_CACHE.move_to_end(cache_key)
            return np.array(_QUERY_VECTOR_CACHE[cache_key], dtype=np.float32)

    vector = np.asarray(model.encode([query], kind="query")[0], dtype=np.float32)

    with _QUERY_VECTOR_CACHE_LOCK:
        _QUERY_VECTOR_CACHE[cache_key] = tuple(vector.tolist())
        _QUERY_VECTOR_CACHE.move_to_end(cache_key)
        if len(_QUERY_VECTOR_CACHE) > _QUERY_VECTOR_CACHE_MAX:
            _QUERY_VECTOR_CACHE.popitem(last=False)

    return vector


OLLAMA_RAG_SYSTEM_PROMPT = (
    "You are an offline student matching assistant. "
    "Rank only the given profiles. Use only profile facts. Never say likely. "
    "Return JSON only: {\"matches\":[{\"STUD_ID\":\"...\",\"score\":0.92,\"reason\":\"short reason\"}]}. "
    "Use scores: 0.85-1 strong, 0.60-0.84 good, 0.30-0.59 weak, 0.0 no evidence."
)


@dataclass(frozen=True)
class SemanticIndexSyncResult:
    total_profiles: int
    embedded_count: int
    skipped_count: int
    model_name: str
    vector_store_name: str


def get_default_vector_store(settings: AppSettings) -> FaissVectorStore:
    return FaissVectorStore(settings.semantic_index_dir, collection_name="students")


def rank_student_rows_by_ollama_rag(
    settings: AppSettings,
    session: Session,
    semantic_filter: SemanticFilter,
    candidate_rows: tuple[StudentCurrent, ...],
    *,
    chat_runner: SemanticChatRunner | None = None,
) -> tuple[SemanticMatch, ...]:
    if not candidate_rows:
        return ()
    if chat_runner is None and settings.runtime_mode == "testing":
        return local_retrieval_estimate(semantic_filter, candidate_rows, "Qwen is skipped in testing runtime")

    profiles = build_student_semantic_profiles(candidate_rows)
    retrieved_profiles = retrieve_rag_candidate_profiles(
        semantic_filter.query,
        profiles,
        candidate_limit=settings.rag_candidate_limit,
    )
    if not retrieved_profiles:
        return ()

    prompt = build_ollama_rag_prompt(
        semantic_filter.query,
        retrieved_profiles,
        top_k=min(semantic_filter.top_k, len(retrieved_profiles)),
        profile_text_limit=settings.rag_profile_text_limit,
    )
    runner = chat_runner or (lambda prompt_text, system_prompt: run_ollama_rag_chat(settings, prompt_text, system_prompt))

    try:
        response_text = runner(prompt, OLLAMA_RAG_SYSTEM_PROMPT)
        candidate_map = build_rag_candidate_map(retrieved_profiles)
        raw_matches = parse_semantic_match_response(
            response_text,
            candidate_map,
            top_k=semantic_filter.top_k,
            minimum_score=None,
        )
        matches = normalize_rag_match_scores(raw_matches)
        return filter_semantic_matches(matches, minimum_score=semantic_filter.minimum_score, top_k=semantic_filter.top_k)
    except Exception as exc:
        return local_retrieval_estimate(semantic_filter, candidate_rows, str(exc))


def retrieve_rag_candidate_profiles(
    query: str,
    profiles: Iterable[StudentSemanticProfile],
    *,
    candidate_limit: int,
) -> tuple[StudentSemanticProfile, ...]:
    profile_tuple = tuple(profiles)
    if candidate_limit <= 0:
        raise ValueError("RAG candidate limit must be positive")
    if len(profile_tuple) <= candidate_limit:
        return profile_tuple

    candidates = tuple(profile_to_semantic_candidate(profile) for profile in profile_tuple)
    ranked = rank_semantic_candidates_locally(query, candidates, top_k=candidate_limit, minimum_score=None)
    if not ranked:
        return profile_tuple[:candidate_limit]

    profiles_by_id = {profile.STUD_ID: profile for profile in profile_tuple}
    ranked_profiles = tuple(profiles_by_id[match.STUD_ID] for match in ranked if match.STUD_ID in profiles_by_id)
    if len(ranked_profiles) >= candidate_limit:
        return ranked_profiles[:candidate_limit]

    ranked_ids = {profile.STUD_ID for profile in ranked_profiles}
    fill_profiles = tuple(profile for profile in profile_tuple if profile.STUD_ID not in ranked_ids)
    return (ranked_profiles + fill_profiles)[:candidate_limit]


def build_ollama_rag_prompt(
    query: str,
    profiles: Iterable[StudentSemanticProfile],
    *,
    top_k: int,
    profile_text_limit: int,
) -> str:
    clean_query = clean_semantic_value(query)
    if not clean_query:
        raise ValueError("RAG query cannot be empty")
    if top_k <= 0:
        raise ValueError("RAG top_k must be positive")

    payload = {
        "request": clean_query,
        "top_k": top_k,
        "score_rules": "0.85-1 strong fit, 0.60-0.84 good fit, 0.30-0.59 weak fit, 0 no evidence",
        "candidates": [
            {
                "STUD_ID": profile.STUD_ID,
                "profile": compact_rag_profile_text(profile, max_length=profile_text_limit),
            }
            for profile in profiles
        ],
    }
    return json.dumps(payload, ensure_ascii=True, indent=2, default=str)


def run_ollama_rag_chat(settings: AppSettings, prompt: str, system_prompt: str | None) -> str:
    return run_ollama_chat(
        prompt,
        base_url=settings.ollama_base_url,
        model_name=settings.ollama_model_name,
        system_prompt=system_prompt,
        timeout_seconds=settings.ollama_request_timeout_seconds,
        response_format="json",
        think=False,
        options={"temperature": 0, "num_predict": 1024, "num_ctx": 8192},
    )


def normalize_rag_match_scores(matches: tuple[SemanticMatch, ...]) -> tuple[SemanticMatch, ...]:
    if not matches or any(match.score > 0 for match in matches):
        return matches

    repaired_matches = []
    for index, match in enumerate(matches):
        repaired_score = max(0.35, 0.9 - (index * 0.1))
        repaired_matches.append(
            SemanticMatch(
                STUD_ID=match.STUD_ID,
                score=round(repaired_score, 6),
                reason=f"{match.reason} Score inferred from Qwen ranking order.",
                document_hash=match.document_hash,
            )
        )
    return tuple(repaired_matches)


def filter_semantic_matches(
    matches: tuple[SemanticMatch, ...],
    *,
    minimum_score: float | None,
    top_k: int,
) -> tuple[SemanticMatch, ...]:
    filtered_matches = tuple(match for match in matches if minimum_score is None or match.score >= minimum_score)
    return tuple(sorted(filtered_matches, key=lambda match: (-match.score, match.STUD_ID))[:top_k])


def compact_rag_profile_text(profile: StudentSemanticProfile, *, max_length: int) -> str:
    parts = [
        ("Major", profile.fields.get("MAJR_DESC")),
        ("Class", profile.fields.get("CLAS_DESC")),
        ("GPA", profile.fields.get("CUM_GPA")),
        ("Probation", profile.fields.get("PROBATION")),
        ("Skills", profile.fields.get("WSP_TECHNICAL_SKILLS")),
        ("Preferred", profile.fields.get("WSP_PREFERRED_TYPE_OF_WORK")),
        ("Previous", profile.fields.get("WSP_PREV_WORK") or profile.fields.get("WSP_PREVIOUS_TYPE_OF_WORK")),
        ("Org", profile.fields.get("WSP_ORGANIZATIONAL_SKILLS")),
    ]
    text = "; ".join(f"{label}: {value}" for label, value in parts if value)
    return truncate_semantic_prompt_text(text or profile.text, max_length=max_length)


def profile_to_semantic_candidate(profile: StudentSemanticProfile) -> SemanticCandidate:
    return SemanticCandidate(
        STUD_ID=profile.STUD_ID,
        text=profile.text,
        fields=(),
        document_hash=profile.document_hash,
    )


def build_rag_candidate_map(profiles: Iterable[StudentSemanticProfile]) -> dict[str, SemanticCandidate]:
    return {profile.STUD_ID: profile_to_semantic_candidate(profile) for profile in profiles}


def sync_student_semantic_index(
    session: Session,
    settings: AppSettings,
    students: Iterable[StudentCurrent],
    *,
    embedding_model: EmbeddingModel | None = None,
    vector_store: FaissVectorStore | None = None,
) -> SemanticIndexSyncResult:
    model = embedding_model or get_default_embedding_model(settings)
    store = vector_store or get_default_vector_store(settings)
    profiles = build_student_semantic_profiles(students)
    existing_rows = load_existing_semantic_rows(session, model.model_name)
    indexed_ids = store.record_ids()

    changed_profiles = tuple(
        profile
        for profile in profiles
        if profile_needs_embedding(profile, existing_rows.get(profile.STUD_ID), indexed_ids)
    )
    if changed_profiles:
        vectors = model.encode([profile.text for profile in changed_profiles], kind="document")
        records = tuple(
            VectorRecord(
                record_id=profile.STUD_ID,
                embedding=vectors[index],
                metadata=profile.metadata | {"semantic_hash": profile.document_hash, "model_name": model.model_name},
                document=profile.text,
            )
            for index, profile in enumerate(changed_profiles)
        )
        store.upsert(records)
        upsert_semantic_embedding_rows(session, changed_profiles, model_name=model.model_name, vector_store_name=store.vector_store_name)

    return SemanticIndexSyncResult(
        total_profiles=len(profiles),
        embedded_count=len(changed_profiles),
        skipped_count=len(profiles) - len(changed_profiles),
        model_name=model.model_name,
        vector_store_name=store.vector_store_name,
    )


def rank_student_rows_by_vector_search(
    settings: AppSettings,
    session: Session,
    semantic_filter: SemanticFilter,
    candidate_rows: tuple[StudentCurrent, ...],
    *,
    embedding_model: EmbeddingModel | None = None,
    vector_store: FaissVectorStore | None = None,
) -> tuple[SemanticMatch, ...]:
    if not candidate_rows:
        return ()

    try:
        query = semantic_filter.query
        model = embedding_model or get_default_embedding_model(settings)
        store = vector_store or get_default_vector_store(settings)
        if not _is_index_fresh() and not _reindex_in_progress():
            sync_student_semantic_index(session, settings, candidate_rows, embedding_model=model, vector_store=store)
        candidate_id_set = {row.STUD_ID for row in candidate_rows}
        query_vector = _get_query_vector(model, query)
        vector_results = store.query(
            np.asarray(query_vector, dtype=np.float32),
            top_k=semantic_filter.top_k,
            candidate_ids=candidate_id_set,
            minimum_score=semantic_filter.minimum_score,
        )
        if not vector_results:
            return ()
        # Build profiles only for matched students, not all candidates
        matched_ids = {r.record_id for r in vector_results}
        matched_rows = tuple(row for row in candidate_rows if row.STUD_ID in matched_ids)
        profiles_by_id = {p.STUD_ID: p for p in build_student_semantic_profiles(matched_rows)}
        return tuple(
            SemanticMatch(
                STUD_ID=result.record_id,
                score=result.score,
                reason=build_local_semantic_explanation(
                    query,
                    profiles_by_id[result.record_id],
                    score=result.score,
                ),
                document_hash=str(result.metadata.get("semantic_hash") or ""),
            )
            for result in vector_results
            if result.record_id in profiles_by_id
        )
    except Exception as exc:
        return text_match_fallback(semantic_filter, candidate_rows, str(exc))


def text_match_fallback(
    semantic_filter: SemanticFilter,
    candidate_rows: tuple[StudentCurrent, ...],
    reason: str,
) -> tuple[SemanticMatch, ...]:
    fallback_matches = rank_student_rows_semantically(
        semantic_filter.query,
        candidate_rows,
        source_fields=semantic_filter.source_fields,
        top_k=semantic_filter.top_k,
        minimum_score=semantic_filter.minimum_score,
    )
    return tuple(
        SemanticMatch(
            STUD_ID=match.STUD_ID,
            score=match.score,
            reason=f"Text match fallback because embedding search was unavailable: {match.reason or reason}",
            document_hash=match.document_hash,
        )
        for match in fallback_matches
    )


def local_retrieval_estimate(
    semantic_filter: SemanticFilter,
    candidate_rows: tuple[StudentCurrent, ...],
    reason: str,
) -> tuple[SemanticMatch, ...]:
    fallback_matches = rank_student_rows_semantically(
        semantic_filter.query,
        candidate_rows,
        source_fields=semantic_filter.source_fields,
        top_k=semantic_filter.top_k,
        minimum_score=semantic_filter.minimum_score,
    )
    return tuple(
        SemanticMatch(
            STUD_ID=match.STUD_ID,
            score=match.score,
            reason=f"Local retrieval estimate while Qwen RAG is unavailable ({reason}): {match.reason}",
            document_hash=match.document_hash,
        )
        for match in fallback_matches
    )


def load_existing_semantic_rows(session: Session, model_name: str) -> dict[str, SemanticEmbedding]:
    rows = (
        session.query(SemanticEmbedding)
        .filter(
            SemanticEmbedding.source_column == SEMANTIC_PROFILE_SOURCE_COLUMN,
            SemanticEmbedding.embedding_model_name == model_name,
        )
        .all()
    )
    return {row.STUD_ID: row for row in rows}


def profile_needs_embedding(
    profile: StudentSemanticProfile,
    row: SemanticEmbedding | None,
    indexed_ids: set[str],
) -> bool:
    if row is None:
        return True
    if row.semantic_document_hash != profile.document_hash:
        return True
    if row.embedding_vector_id != profile.STUD_ID:
        return True
    if profile.STUD_ID not in indexed_ids:
        return True
    return False


def upsert_semantic_embedding_rows(
    session: Session,
    profiles: Iterable[StudentSemanticProfile],
    *,
    model_name: str,
    vector_store_name: str = DEFAULT_VECTOR_STORE_NAME,
) -> None:
    # Remove rows from any previous model so the UNIQUE constraint on embedding_vector_id
    # is never violated when switching embedding models.
    session.query(SemanticEmbedding).filter(
        SemanticEmbedding.embedding_model_name != model_name
    ).delete(synchronize_session=False)

    existing_rows = load_existing_semantic_rows(session, model_name)
    for profile in profiles:
        row = existing_rows.get(profile.STUD_ID)
        if row is None:
            session.add(
                SemanticEmbedding(
                    STUD_ID=profile.STUD_ID,
                    source_column=SEMANTIC_PROFILE_SOURCE_COLUMN,
                    source_text=profile.text,
                    semantic_document_hash=profile.document_hash,
                    embedding_vector_id=profile.STUD_ID,
                    embedding_model_name=model_name,
                    vector_store_name=vector_store_name,
                )
            )
        else:
            row.source_text = profile.text
            row.semantic_document_hash = profile.document_hash
            row.embedding_vector_id = profile.STUD_ID
            row.vector_store_name = vector_store_name
    session.flush()
