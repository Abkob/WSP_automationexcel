from __future__ import annotations

import pytest

from config import AppSettings
from database.db import create_session_factory, create_sqlite_engine, initialize_database
from database.models import StudentCurrent
from services.semantic_service import (
    OllamaModelError,
    SemanticCandidate,
    SemanticMatch,
    SemanticTextField,
    build_semantic_ranking_prompt,
    build_student_semantic_document,
    build_student_semantic_text,
    build_semantic_candidate_map,
    check_ollama_model_availability,
    check_semantic_model_status,
    clean_semantic_value,
    ensure_ollama_model_available,
    ensure_semantic_artifact_directory,
    get_semantic_candidates,
    hash_semantic_document,
    humanize_field_name,
    is_private_semantic_field,
    ollama_api_url,
    parse_semantic_match_response,
    parse_semantic_score,
    rank_semantic_candidates_locally,
    rank_semantic_candidates,
    rank_student_rows_semantically,
    run_ollama_chat,
    select_semantic_candidates_for_query,
    semantic_query_tokens,
    truncate_semantic_prompt_text,
)


def test_text_builder_includes_expected_non_private_fields() -> None:
    student = StudentCurrent(
        STUD_ID="1001",
        STUD_NAME="Private Name",
        STUD_EMAIL="private@example.com",
        MOBILE_NBR="70123456",
        MAJR_DESC="Computer Science",
        CLAS_DESC="Senior",
        STST_DESC="Active",
        STYP_DESC="Regular",
        WSP_WRITTEN_LANGUAGES="English",
        WSP_SPOKEN_LANGUAGES="English, Arabic",
        WSP_ORGANIZATIONAL_SKILLS="Planning",
        WSP_TECHNICAL_SKILLS="Python, Excel",
        WSP_INTERPERSONAL_SKILLS="Teamwork",
        WSP_ADDITIONAL_SKILLS="Documentation",
        WSP_PREV_WORK="Office assistant",
        WSP_PREVIOUS_TYPE_OF_WORK="Administrative",
        WSP_PREFERRED_TYPE_OF_WORK="Data analysis",
    )

    document = build_student_semantic_document(student)

    assert document.STUD_ID == "1001"
    assert "Major: Computer Science" in document.text
    assert "Technical skills: Python, Excel" in document.text
    assert "Spoken languages: English, Arabic" in document.text
    assert "Previous work: Office assistant" in document.text
    assert "Preferred type of work: Data analysis" in document.text
    assert "Private Name" not in document.text
    assert "private@example.com" not in document.text
    assert "70123456" not in document.text


def test_empty_fields_do_not_create_noisy_text() -> None:
    student = StudentCurrent(
        STUD_ID="1002",
        MAJR_DESC="  ",
        WSP_TECHNICAL_SKILLS=None,
        WSP_SPOKEN_LANGUAGES="",
        extra_columns_json={"EMPTY_EXTRA": "   "},
    )

    document = build_student_semantic_document(student)

    assert document.text == ""
    assert document.fields == ()


def test_text_builder_output_is_stable() -> None:
    student = StudentCurrent(
        STUD_ID="1003",
        MAJR_DESC="Business",
        WSP_TECHNICAL_SKILLS="Excel",
        WSP_ADDITIONAL_SKILLS="Filing",
        WSP_PREFERRED_TYPE_OF_WORK="Admin",
        extra_columns_json={"Z_GOAL": "Research", "A_NOTE": "Available evenings"},
    )

    document = build_student_semantic_document(student)

    assert document.fields == (
        SemanticTextField("MAJR_DESC", "Major", "Business"),
        SemanticTextField("WSP_TECHNICAL_SKILLS", "Technical skills", "Excel"),
        SemanticTextField("WSP_ADDITIONAL_SKILLS", "Additional skills", "Filing"),
        SemanticTextField("WSP_PREFERRED_TYPE_OF_WORK", "Preferred type of work", "Admin"),
        SemanticTextField("A_NOTE", "A Note", "Available evenings"),
        SemanticTextField("Z_GOAL", "Z Goal", "Research"),
    )
    assert document.text == "\n".join(
        [
            "Major: Business",
            "Technical skills: Excel",
            "Additional skills: Filing",
            "Preferred type of work: Admin",
            "A Note: Available evenings",
            "Z Goal: Research",
        ]
    )


def test_source_fields_can_select_private_fields_when_explicitly_needed() -> None:
    student = StudentCurrent(
        STUD_ID="1004",
        STUD_NAME="Alice Example",
        STUD_EMAIL="alice@example.com",
        WSP_TECHNICAL_SKILLS="Python",
    )

    default_text = build_student_semantic_text(student, source_fields=("STUD_NAME", "STUD_EMAIL", "WSP_TECHNICAL_SKILLS"))
    private_text = build_student_semantic_text(
        student,
        include_private_fields=True,
        source_fields=("STUD_NAME", "STUD_EMAIL", "WSP_TECHNICAL_SKILLS"),
    )

    assert default_text == "Technical skills: Python"
    assert "Student name: Alice Example" in private_text
    assert "Student email: alice@example.com" in private_text


def test_extra_columns_are_included_without_overwriting_raw_values() -> None:
    extra_columns = {
        "CAREER_GOALS": "  data   reporting  ",
        "ALT_EMAIL": "hidden@example.com",
    }
    student = StudentCurrent(STUD_ID="1005", extra_columns_json=extra_columns)

    document = build_student_semantic_document(student)

    assert "Career Goals: data reporting" in document.text
    assert "hidden@example.com" not in document.text
    assert extra_columns["CAREER_GOALS"] == "  data   reporting  "


def test_source_fields_can_disable_automatic_extra_columns() -> None:
    student = StudentCurrent(
        STUD_ID="1006",
        WSP_TECHNICAL_SKILLS="SQL",
        extra_columns_json={"CAREER_GOALS": "Analytics"},
    )

    text = build_student_semantic_text(student, source_fields=("WSP_TECHNICAL_SKILLS",))

    assert text == "Technical skills: SQL"


def test_clean_semantic_value_handles_common_values() -> None:
    assert clean_semantic_value(None) == ""
    assert clean_semantic_value(True) == "Yes"
    assert clean_semantic_value(False) == "No"
    assert clean_semantic_value("  Python \n Excel\tSQL  ") == "Python Excel SQL"
    assert clean_semantic_value(3.5) == "3.5"


def test_private_field_detection_and_human_labels() -> None:
    assert is_private_semantic_field("STUD_EMAIL")
    assert is_private_semantic_field("PARENT_PHONE")
    assert is_private_semantic_field("CONTACT_NAME")
    assert not is_private_semantic_field("CAREER_GOALS")
    assert humanize_field_name("WSP_TECHNICAL_SKILLS") == "Technical Skills"
    assert humanize_field_name("CAREER_GOALS") == "Career Goals"


def test_ollama_api_url_normalizes_base_url() -> None:
    assert ollama_api_url("http://localhost:11434/", "api/tags") == "http://localhost:11434/api/tags"


def test_ollama_availability_detects_installed_model() -> None:
    calls: list[tuple[str, float]] = []

    def fake_get(url: str, timeout: float) -> dict:
        calls.append((url, timeout))
        return {"models": [{"name": "qwen3:8b"}, {"name": "llama3.2"}]}

    status = check_ollama_model_availability(timeout_seconds=7.0, http_get=fake_get)

    assert calls == [("http://localhost:11434/api/tags", 7.0)]
    assert status.enabled is True
    assert status.server_available is True
    assert status.model_available is True
    assert status.available_models == ("llama3.2", "qwen3:8b")
    assert status.error_message is None


def test_ollama_availability_reports_missing_server() -> None:
    def fake_get(_url: str, _timeout: float) -> dict:
        raise OllamaModelError("connection refused")

    status = check_ollama_model_availability(http_get=fake_get)

    assert status.server_available is False
    assert status.model_available is False
    assert "Install/start Ollama" in (status.error_message or "")
    assert "ollama run qwen3:8b" in (status.error_message or "")


def test_ollama_availability_reports_missing_model() -> None:
    def fake_get(_url: str, _timeout: float) -> dict:
        return {"models": [{"name": "another-model"}]}

    status = check_ollama_model_availability(http_get=fake_get)

    assert status.server_available is True
    assert status.model_available is False
    assert status.available_models == ("another-model",)
    assert "ollama run qwen3:8b" in (status.error_message or "")


def test_ensure_ollama_model_available_raises_clear_error() -> None:
    def fake_get(_url: str, _timeout: float) -> dict:
        return {"models": []}

    status = check_ollama_model_availability(http_get=fake_get)

    with pytest.raises(OllamaModelError, match="qwen3:8b"):
        ensure_ollama_model_available(status)


def test_disabled_semantic_search_does_not_call_ollama(tmp_path) -> None:
    settings = AppSettings(data_dir=tmp_path, runtime_mode="testing", semantic_search_enabled=False)

    def fake_get(_url: str, _timeout: float) -> dict:
        raise AssertionError("Ollama should not be called when semantic search is disabled")

    status = check_semantic_model_status(settings, http_get=fake_get)

    assert status.enabled is False
    assert status.error_message == "Semantic search is disabled."


def test_enabled_semantic_search_uses_settings(tmp_path) -> None:
    settings = AppSettings(
        data_dir=tmp_path,
        runtime_mode="testing",
        semantic_search_enabled=True,
        ollama_base_url="http://localhost:11435/",
        ollama_model_name="custom-model",
        ollama_request_timeout_seconds=2.5,
    )
    calls: list[tuple[str, float]] = []

    def fake_get(url: str, timeout: float) -> dict:
        calls.append((url, timeout))
        return {"models": [{"name": "custom-model"}]}

    status = check_semantic_model_status(settings, http_get=fake_get)

    assert calls == [("http://localhost:11435/api/tags", 2.5)]
    assert status.model_name == "custom-model"
    assert status.model_available is True


def test_run_ollama_chat_uses_mocked_client() -> None:
    calls: list[tuple[str, dict, float]] = []

    def fake_post(url: str, payload: dict, timeout: float) -> dict:
        calls.append((url, payload, timeout))
        return {"message": {"content": "Match"}}

    response = run_ollama_chat(
        "does this student match data analysis?",
        system_prompt="Answer briefly.",
        timeout_seconds=4.0,
        http_post=fake_post,
    )

    assert response == "Match"
    assert calls[0][0] == "http://localhost:11434/api/chat"
    assert calls[0][1]["model"] == "qwen3:8b"
    assert calls[0][1]["stream"] is False
    assert calls[0][1]["think"] is False
    assert calls[0][1]["messages"] == [
        {"role": "system", "content": "Answer briefly."},
        {"role": "user", "content": "does this student match data analysis?"},
    ]
    assert calls[0][2] == 4.0


def test_run_ollama_chat_can_request_json_format_and_options() -> None:
    calls: list[tuple[str, dict, float]] = []

    def fake_post(url: str, payload: dict, timeout: float) -> dict:
        calls.append((url, payload, timeout))
        return {"message": {"content": '{"ok": true}'}}

    response = run_ollama_chat(
        "return json",
        response_format="json",
        options={"temperature": 0, "num_predict": 10},
        http_post=fake_post,
    )

    assert response == '{"ok": true}'
    assert calls[0][1]["format"] == "json"
    assert calls[0][1]["options"] == {"temperature": 0, "num_predict": 10}


def test_run_ollama_chat_rejects_empty_prompt_or_response() -> None:
    with pytest.raises(OllamaModelError, match="prompt cannot be empty"):
        run_ollama_chat("   ", http_post=lambda _url, _payload, _timeout: {})

    with pytest.raises(OllamaModelError, match="empty chat response"):
        run_ollama_chat("hello", http_post=lambda _url, _payload, _timeout: {"message": {"content": "   "}})


def test_semantic_candidates_return_current_non_blank_students(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add_all(
            [
                StudentCurrent(STUD_ID="1002", WSP_TECHNICAL_SKILLS="Excel"),
                StudentCurrent(STUD_ID="1001", WSP_TECHNICAL_SKILLS="Python"),
                StudentCurrent(STUD_ID="1003", WSP_TECHNICAL_SKILLS="   "),
                StudentCurrent(STUD_ID="1004", WSP_TECHNICAL_SKILLS="SQL", missing_from_latest_import=True),
            ]
        )
        session.commit()

    with session_factory() as session:
        candidates = get_semantic_candidates(session)

    assert [candidate.STUD_ID for candidate in candidates] == ["1001", "1002"]
    assert candidates[0].text == "Technical skills: Python"
    assert len(candidates[0].document_hash) == 64


def test_semantic_candidates_can_include_missing_students(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add_all(
            [
                StudentCurrent(STUD_ID="1001", WSP_TECHNICAL_SKILLS="Python"),
                StudentCurrent(STUD_ID="1002", WSP_TECHNICAL_SKILLS="SQL", missing_from_latest_import=True),
            ]
        )
        session.commit()

    with session_factory() as session:
        candidates = get_semantic_candidates(session, include_missing=True)

    assert [candidate.STUD_ID for candidate in candidates] == ["1001", "1002"]


def test_semantic_candidates_support_source_fields_and_student_id_subset(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add_all(
            [
                StudentCurrent(STUD_ID="1001", WSP_TECHNICAL_SKILLS="Python", WSP_PREFERRED_TYPE_OF_WORK="Research"),
                StudentCurrent(STUD_ID="1002", WSP_TECHNICAL_SKILLS="Excel", WSP_PREFERRED_TYPE_OF_WORK="Admin"),
                StudentCurrent(STUD_ID="1003", WSP_TECHNICAL_SKILLS="SQL", WSP_PREFERRED_TYPE_OF_WORK="Data"),
            ]
        )
        session.commit()

    with session_factory() as session:
        candidates = get_semantic_candidates(
            session,
            source_fields=("WSP_PREFERRED_TYPE_OF_WORK",),
            student_ids=("1003", "1001"),
        )

    assert [candidate.STUD_ID for candidate in candidates] == ["1001", "1003"]
    assert [candidate.text for candidate in candidates] == [
        "Preferred type of work: Research",
        "Preferred type of work: Data",
    ]


def test_semantic_candidate_map_uses_student_id() -> None:
    student = StudentCurrent(STUD_ID="1001", WSP_TECHNICAL_SKILLS="Python")
    document = build_student_semantic_document(student)
    candidates = get_semantic_candidates_from_documents_for_test(document)

    mapping = build_semantic_candidate_map(candidates)

    assert tuple(mapping) == ("1001",)
    assert mapping["1001"].text == "Technical skills: Python"


def test_semantic_document_hash_is_stable_and_changes_with_text() -> None:
    first = build_student_semantic_document(StudentCurrent(STUD_ID="1001", WSP_TECHNICAL_SKILLS="Python"))
    same = build_student_semantic_document(StudentCurrent(STUD_ID="1001", WSP_TECHNICAL_SKILLS="Python"))
    changed = build_student_semantic_document(StudentCurrent(STUD_ID="1001", WSP_TECHNICAL_SKILLS="Python, SQL"))

    assert hash_semantic_document(first) == hash_semantic_document(same)
    assert hash_semantic_document(first) != hash_semantic_document(changed)


def test_semantic_artifact_directory_can_be_created(tmp_path) -> None:
    settings = AppSettings(data_dir=tmp_path / "data", runtime_mode="testing")

    path = ensure_semantic_artifact_directory(settings)

    assert path == settings.semantic_index_dir
    assert path.exists()
    assert path.is_dir()


def test_semantic_ranking_prompt_contains_query_candidates_and_json_contract() -> None:
    candidates = (
        SemanticCandidate("1001", "Technical skills: Python", (), "hash-1"),
        SemanticCandidate("1002", "Technical skills: Excel", (), "hash-2"),
    )

    prompt = build_semantic_ranking_prompt("data analysis", candidates, top_k=1, minimum_score=0.5)

    assert '"query": "data analysis"' in prompt
    assert '"STUD_ID": "1001"' in prompt
    assert '"Technical skills: Python"' in prompt
    assert '"minimum_score": 0.5' in prompt
    assert '"matches"' in prompt


def test_semantic_ranking_prompt_truncates_long_candidate_text() -> None:
    long_text = "Technical skills: " + ("Excel reporting " * 100)
    prompt = build_semantic_ranking_prompt(
        "spreadsheet reporting",
        (SemanticCandidate("1001", long_text, (), "hash-1"),),
        top_k=1,
    )

    assert len(truncate_semantic_prompt_text(long_text)) <= 220
    assert "..." in prompt
    assert len(prompt) < len(long_text)


def test_parse_semantic_score_accepts_zero_to_one_and_percent_values() -> None:
    assert parse_semantic_score(0.91) == 0.91
    assert parse_semantic_score("0.75") == 0.75
    assert parse_semantic_score("83") == 0.83
    assert parse_semantic_score(True) is None
    assert parse_semantic_score("-1") is None
    assert parse_semantic_score("bad") is None


def test_parse_semantic_match_response_filters_sorts_and_limits_matches() -> None:
    candidates = (
        SemanticCandidate("1001", "Technical skills: Python", (), "hash-1"),
        SemanticCandidate("1002", "Technical skills: Excel", (), "hash-2"),
        SemanticCandidate("1003", "Technical skills: SQL", (), "hash-3"),
    )
    response = """
    ```json
    {
      "matches": [
        {"STUD_ID": "1001", "score": 0.72, "reason": "some fit"},
        {"STUD_ID": "UNKNOWN", "score": 0.99, "reason": "not a candidate"},
        {"STUD_ID": "1002", "score": 91, "reason": "best fit"},
        {"STUD_ID": "1003", "score": 0.30, "reason": "too low"}
      ]
    }
    ```
    """

    matches = parse_semantic_match_response(
        response,
        build_semantic_candidate_map(candidates),
        top_k=2,
        minimum_score=0.5,
    )

    assert matches == (
        SemanticMatch("1002", 0.91, "best fit", "hash-2"),
        SemanticMatch("1001", 0.72, "some fit", "hash-1"),
    )


def test_parse_semantic_match_response_rejects_invalid_json() -> None:
    with pytest.raises(OllamaModelError, match="did not contain JSON"):
        parse_semantic_match_response("not json", {}, top_k=10)


def test_rank_semantic_candidates_uses_mocked_chat_runner() -> None:
    candidates = (
        SemanticCandidate("1001", "Technical skills: Python", (), "hash-1"),
        SemanticCandidate("1002", "Technical skills: Excel", (), "hash-2"),
    )
    calls: list[tuple[str, str | None]] = []

    def fake_chat(prompt: str, system_prompt: str | None) -> str:
        calls.append((prompt, system_prompt))
        return '{"matches": [{"STUD_ID": "1002", "score": 0.88, "reason": "spreadsheet fit"}]}'

    matches = rank_semantic_candidates("spreadsheet work", candidates, top_k=5, chat_runner=fake_chat)

    assert len(calls) == 1
    assert "spreadsheet work" in calls[0][0]
    assert "rank student profiles" in (calls[0][1] or "").lower()
    assert matches == (SemanticMatch("1002", 0.88, "spreadsheet fit", "hash-2"),)


def test_rank_semantic_candidates_defaults_to_functional_offline_ranker() -> None:
    candidates = (
        SemanticCandidate("1001", "Preferred type of work: event support and registration desk", (), "hash-1"),
        SemanticCandidate(
            "1002",
            "Technical skills: Excel, SQL, spreadsheet QA\nPreferred type of work: Data entry and spreadsheet reporting",
            (
                SemanticTextField("WSP_TECHNICAL_SKILLS", "Technical skills", "Excel, SQL, spreadsheet QA"),
                SemanticTextField("WSP_PREFERRED_TYPE_OF_WORK", "Preferred type of work", "Data entry and spreadsheet reporting"),
            ),
            "hash-2",
        ),
        SemanticCandidate("1003", "Technical skills: lab logs and sample labels", (), "hash-3"),
    )

    matches = rank_semantic_candidates("spreadsheet reporting with careful data entry", candidates, top_k=3, minimum_score=0.1)

    assert matches[0].STUD_ID == "1002"
    assert matches[0].score >= 0.4
    assert "Preferred type of work" in matches[0].reason


def test_local_semantic_ranker_scores_synonyms_and_respects_minimum_score() -> None:
    candidates = (
        SemanticCandidate(
            "1001",
            "Technical skills: Excel pivot tables\nPreferred type of work: dashboard summaries",
            (
                SemanticTextField("WSP_TECHNICAL_SKILLS", "Technical skills", "Excel pivot tables"),
                SemanticTextField("WSP_PREFERRED_TYPE_OF_WORK", "Preferred type of work", "dashboard summaries"),
            ),
            "hash-1",
        ),
        SemanticCandidate(
            "1002",
            "Technical skills: microscope safety logs\nPreferred type of work: lab preparation",
            (
                SemanticTextField("WSP_TECHNICAL_SKILLS", "Technical skills", "microscope safety logs"),
                SemanticTextField("WSP_PREFERRED_TYPE_OF_WORK", "Preferred type of work", "lab preparation"),
            ),
            "hash-2",
        ),
    )

    matches = rank_semantic_candidates_locally("spreadsheet analytics", candidates, top_k=5, minimum_score=0.1)

    assert [match.STUD_ID for match in matches] == ["1001"]
    assert matches[0].reason.startswith("Matched")


def test_default_semantic_ranker_does_not_cap_local_results_to_qwen_prompt_limit() -> None:
    candidates = tuple(
        SemanticCandidate(
            str(1000 + index),
            f"Technical skills: Excel spreadsheet reporting item {index}",
            (SemanticTextField("WSP_TECHNICAL_SKILLS", "Technical skills", f"Excel spreadsheet reporting item {index}"),),
            f"hash-{index}",
        )
        for index in range(8)
    )

    matches = rank_semantic_candidates("spreadsheet reporting", candidates, top_k=8)

    assert len(matches) == 8


def test_semantic_query_tokens_remove_short_words_and_stop_words() -> None:
    assert semantic_query_tokens("the spreadsheet and careful data entry work") == (
        "spreadsheet",
        "careful",
        "data",
        "entry",
    )


def test_select_semantic_candidates_prefers_lexically_relevant_profiles() -> None:
    candidates = (
        SemanticCandidate("1001", "Preferred type of work: event usher", (), "hash-1"),
        SemanticCandidate("1002", "Technical skills: Excel spreadsheets and reporting dashboards", (), "hash-2"),
        SemanticCandidate("1003", "Preferred type of work: careful office data entry", (), "hash-3"),
        SemanticCandidate("1004", "Technical skills: lab safety and sample labeling", (), "hash-4"),
    )

    selected = select_semantic_candidates_for_query(
        "spreadsheet reporting with careful data entry",
        candidates,
        max_candidates=2,
    )

    assert [candidate.STUD_ID for candidate in selected] == ["1003", "1002"]


def test_rank_semantic_candidates_limits_prompt_candidates_before_qwen_call() -> None:
    candidates = (
        SemanticCandidate("1001", "Technical skills: lab safety", (), "hash-1"),
        SemanticCandidate("1002", "Technical skills: Excel spreadsheet reporting", (), "hash-2"),
        SemanticCandidate("1003", "Technical skills: event coordination", (), "hash-3"),
    )

    def fake_chat(prompt: str, _system_prompt: str | None) -> str:
        assert '"STUD_ID": "1002"' in prompt
        assert '"STUD_ID": "1001"' not in prompt
        assert '"STUD_ID": "1003"' not in prompt
        return '{"matches": [{"STUD_ID": "1002", "score": 0.9, "reason": "spreadsheet reporting"}]}'

    matches = rank_semantic_candidates(
        "spreadsheet reporting",
        candidates,
        top_k=1,
        max_candidates=1,
        chat_runner=fake_chat,
    )

    assert matches == (SemanticMatch("1002", 0.9, "spreadsheet reporting", "hash-2"),)


def test_rank_student_rows_semantically_builds_candidates_from_rows() -> None:
    students = (
        StudentCurrent(STUD_ID="1001", WSP_TECHNICAL_SKILLS="Python"),
        StudentCurrent(STUD_ID="1002", WSP_TECHNICAL_SKILLS="Excel"),
    )

    def fake_chat(_prompt: str, _system_prompt: str | None) -> str:
        return '{"matches": [{"STUD_ID": "1001", "score": 0.9, "reason": "coding"}]}'

    matches = rank_student_rows_semantically(
        "coding",
        students,
        source_fields=("WSP_TECHNICAL_SKILLS",),
        chat_runner=fake_chat,
    )

    assert matches[0].STUD_ID == "1001"
    assert matches[0].score == 0.9


def get_semantic_candidates_from_documents_for_test(document):
    from services.semantic_service import SemanticCandidate

    return (
        SemanticCandidate(
            STUD_ID=document.STUD_ID,
            text=document.text,
            fields=document.fields,
            document_hash=hash_semantic_document(document),
        ),
    )
