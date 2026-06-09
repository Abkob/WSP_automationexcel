from __future__ import annotations

import json
import re
from hashlib import sha256
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable
from urllib import error, request

from sqlalchemy import asc
from sqlalchemy.orm import Session

from config import AppSettings
from database.models import StudentCurrent


DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL_NAME = "qwen3:8b"
DEFAULT_OLLAMA_TIMEOUT_SECONDS = 120.0
OLLAMA_BACKEND_NAME = "ollama"

DEFAULT_SEMANTIC_TEXT_FIELDS = (
    "MAJR_DESC",
    "CLAS_DESC",
    "STST_DESC",
    "STYP_DESC",
    "WSP_WRITTEN_LANGUAGES",
    "WSP_SPOKEN_LANGUAGES",
    "WSP_ORGANIZATIONAL_SKILLS",
    "WSP_TECHNICAL_SKILLS",
    "WSP_INTERPERSONAL_SKILLS",
    "WSP_ADDITIONAL_SKILLS",
    "WSP_PREV_WORK",
    "WSP_PREVIOUS_TYPE_OF_WORK",
    "WSP_PREFERRED_TYPE_OF_WORK",
)
DEFAULT_SEMANTIC_RANKING_CANDIDATE_LIMIT = 4
DEFAULT_SEMANTIC_PROMPT_TEXT_LIMIT = 220

PRIVATE_SEMANTIC_TEXT_FIELDS = (
    "STUD_ID",
    "STUD_NAME",
    "STUD_EMAIL",
    "MOBILE_NBR",
)

FIELD_LABELS = {
    "MAJR_DESC": "Major",
    "CLAS_DESC": "Class",
    "STST_DESC": "Student status",
    "STYP_DESC": "Student type",
    "STUD_ID": "Student ID",
    "STUD_NAME": "Student name",
    "STUD_EMAIL": "Student email",
    "MOBILE_NBR": "Mobile number",
    "WSP_WRITTEN_LANGUAGES": "Written languages",
    "WSP_SPOKEN_LANGUAGES": "Spoken languages",
    "WSP_ORGANIZATIONAL_SKILLS": "Organizational skills",
    "WSP_TECHNICAL_SKILLS": "Technical skills",
    "WSP_INTERPERSONAL_SKILLS": "Interpersonal skills",
    "WSP_ADDITIONAL_SKILLS": "Additional skills",
    "WSP_PREV_WORK": "Previous work",
    "WSP_PREVIOUS_TYPE_OF_WORK": "Previous type of work",
    "WSP_PREFERRED_TYPE_OF_WORK": "Preferred type of work",
}

PRIVATE_FIELD_TOKENS = ("EMAIL", "MOBILE", "PHONE", "NAME", "STUD_ID")
WHITESPACE_RE = re.compile(r"\s+")
SEMANTIC_TOKEN_RE = re.compile(r"[A-Za-z0-9]+")
SEMANTIC_QUERY_STOP_WORDS = {
    "and",
    "are",
    "for",
    "has",
    "have",
    "the",
    "this",
    "with",
    "work",
    "worker",
}
LOCAL_SEMANTIC_FIELD_WEIGHTS = {
    "WSP_PREFERRED_TYPE_OF_WORK": 2.2,
    "WSP_TECHNICAL_SKILLS": 2.0,
    "WSP_PREV_WORK": 1.6,
    "WSP_PREVIOUS_TYPE_OF_WORK": 1.6,
    "WSP_ADDITIONAL_SKILLS": 1.3,
    "WSP_ORGANIZATIONAL_SKILLS": 1.2,
    "WSP_INTERPERSONAL_SKILLS": 1.1,
    "MAJR_DESC": 0.8,
    "CLAS_DESC": 0.5,
    "STST_DESC": 0.4,
    "STYP_DESC": 0.4,
    "WSP_WRITTEN_LANGUAGES": 0.3,
    "WSP_SPOKEN_LANGUAGES": 0.3,
}
LOCAL_SEMANTIC_SYNONYMS = {
    "admin": ("administrative", "office", "forms", "records"),
    "analysis": ("analytics", "reporting", "summary", "dashboard", "dashboards"),
    "assistant": ("support", "helper", "aide"),
    "budget": ("budgets", "invoice", "invoices", "quickbooks", "accounting"),
    "careful": ("accurate", "accuracy", "detail", "details", "quality", "review", "checks", "checking"),
    "clean": ("cleanup", "cleaning", "quality", "qa"),
    "data": ("dataset", "datasets", "entry", "record", "records", "forms", "spreadsheet", "excel"),
    "design": ("canva", "poster", "posters", "social", "media"),
    "entry": ("forms", "record", "records", "review", "checking", "cleanup"),
    "event": ("events", "registration", "desk", "coordination", "volunteers"),
    "excel": ("spreadsheet", "spreadsheets", "sheet", "sheets", "pivot", "tables", "workbook"),
    "lab": ("laboratory", "sample", "samples", "safety", "logs"),
    "research": ("literature", "summary", "summaries", "interviews", "dataset", "datasets"),
    "report": ("reporting", "reports", "dashboard", "dashboards", "summary", "summaries"),
    "reporting": ("report", "reports", "dashboard", "dashboards", "summary", "summaries", "analytics"),
    "spreadsheet": ("excel", "spreadsheets", "sheet", "sheets", "pivot", "tables", "workbook", "qa"),
    "sql": ("database", "data", "query", "queries"),
    "student": ("students", "peer", "campus"),
    "technical": ("it", "support", "troubleshooting", "software"),
    "tutor": ("tutoring", "teaching", "mentor", "mentoring"),
}
JsonGetter = Callable[[str, float], dict[str, Any]]
JsonPoster = Callable[[str, dict[str, Any], float], dict[str, Any]]
SemanticChatRunner = Callable[[str, str | None], str]

SEMANTIC_RANKER_SYSTEM_PROMPT = (
    "You rank student profiles against a user query. "
    "Return JSON only, with a top-level matches array. "
    "Each match must have STUD_ID, score from 0 to 1, and a short reason. "
    "Do not explain your reasoning."
)


class OllamaModelError(RuntimeError):
    """Raised when the local Ollama semantic model cannot be used."""


@dataclass(frozen=True)
class SemanticTextField:
    field_name: str
    label: str
    value: str


@dataclass(frozen=True)
class SemanticTextDocument:
    STUD_ID: str
    text: str
    fields: tuple[SemanticTextField, ...]


@dataclass(frozen=True)
class SemanticCandidate:
    STUD_ID: str
    text: str
    fields: tuple[SemanticTextField, ...]
    document_hash: str


@dataclass(frozen=True)
class SemanticMatch:
    STUD_ID: str
    score: float
    reason: str
    document_hash: str | None = None


@dataclass(frozen=True)
class OllamaModelStatus:
    enabled: bool
    base_url: str
    model_name: str
    server_available: bool
    model_available: bool
    available_models: tuple[str, ...] = ()
    error_message: str | None = None

    @property
    def run_command(self) -> str:
        return f"ollama run {self.model_name}"


def build_student_semantic_document(
    student: StudentCurrent,
    *,
    include_private_fields: bool = False,
    source_fields: Iterable[str] | None = None,
    include_extra_columns: bool = True,
) -> SemanticTextDocument:
    field_names = tuple(source_fields) if source_fields is not None else default_semantic_field_names(student, include_extra_columns)
    fields: list[SemanticTextField] = []

    for field_name in field_names:
        if not include_private_fields and is_private_semantic_field(field_name):
            continue

        value = clean_semantic_value(read_student_value(student, field_name))
        if not value:
            continue

        fields.append(
            SemanticTextField(
                field_name=field_name,
                label=semantic_field_label(field_name),
                value=value,
            )
        )

    return SemanticTextDocument(
        STUD_ID=clean_semantic_value(getattr(student, "STUD_ID", "")),
        text=format_semantic_fields(fields),
        fields=tuple(fields),
    )


def build_student_semantic_text(
    student: StudentCurrent,
    *,
    include_private_fields: bool = False,
    source_fields: Iterable[str] | None = None,
    include_extra_columns: bool = True,
) -> str:
    return build_student_semantic_document(
        student,
        include_private_fields=include_private_fields,
        source_fields=source_fields,
        include_extra_columns=include_extra_columns,
    ).text


def get_semantic_candidates(
    session: Session,
    *,
    include_missing: bool = False,
    source_fields: Iterable[str] | None = None,
    include_private_fields: bool = False,
    include_extra_columns: bool = True,
    student_ids: Iterable[str] | None = None,
) -> tuple[SemanticCandidate, ...]:
    query = session.query(StudentCurrent)
    if not include_missing:
        query = query.filter(StudentCurrent.missing_from_latest_import.is_(False))
    if student_ids is not None:
        query = query.filter(StudentCurrent.STUD_ID.in_(tuple(student_ids)))

    candidates = []
    for student in query.order_by(asc(StudentCurrent.STUD_ID)).all():
        document = build_student_semantic_document(
            student,
            include_private_fields=include_private_fields,
            source_fields=source_fields,
            include_extra_columns=include_extra_columns,
        )
        if not document.text:
            continue
        candidates.append(
            SemanticCandidate(
                STUD_ID=document.STUD_ID,
                text=document.text,
                fields=document.fields,
                document_hash=hash_semantic_document(document),
            )
        )

    return tuple(candidates)


def build_semantic_candidates_from_students(
    students: Iterable[StudentCurrent],
    *,
    source_fields: Iterable[str] | None = None,
    include_private_fields: bool = False,
    include_extra_columns: bool = True,
) -> tuple[SemanticCandidate, ...]:
    candidates = []
    for student in students:
        document = build_student_semantic_document(
            student,
            include_private_fields=include_private_fields,
            source_fields=source_fields,
            include_extra_columns=include_extra_columns,
        )
        if not document.text:
            continue
        candidates.append(
            SemanticCandidate(
                STUD_ID=document.STUD_ID,
                text=document.text,
                fields=document.fields,
                document_hash=hash_semantic_document(document),
            )
        )
    return tuple(candidates)


def build_semantic_candidate_map(candidates: Iterable[SemanticCandidate]) -> dict[str, SemanticCandidate]:
    return {candidate.STUD_ID: candidate for candidate in candidates}


def hash_semantic_document(document: SemanticTextDocument) -> str:
    payload = json.dumps(
        {
            "STUD_ID": document.STUD_ID,
            "text": document.text,
            "fields": [
                {"field_name": field.field_name, "label": field.label, "value": field.value}
                for field in document.fields
            ],
        },
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    )
    return sha256(payload.encode("utf-8")).hexdigest()


def ensure_semantic_artifact_directory(settings: AppSettings) -> Path:
    settings.semantic_index_dir.mkdir(parents=True, exist_ok=True)
    return settings.semantic_index_dir


def build_semantic_ranking_prompt(
    query: str,
    candidates: Iterable[SemanticCandidate],
    *,
    top_k: int,
    minimum_score: float | None = None,
) -> str:
    clean_query = clean_semantic_value(query)
    if not clean_query:
        raise OllamaModelError("Semantic query cannot be empty.")
    if top_k <= 0:
        raise OllamaModelError("Semantic top_k must be positive.")
    validate_minimum_score(minimum_score)

    payload = {
        "query": clean_query,
        "top_k": top_k,
        "minimum_score": minimum_score,
        "candidates": [
            {"STUD_ID": candidate.STUD_ID, "text": truncate_semantic_prompt_text(candidate.text)}
            for candidate in candidates
        ],
        "response_format": {
            "matches": [
                {"STUD_ID": "student id from candidates", "score": 0.0, "reason": "brief reason"}
            ]
        },
    }
    return json.dumps(payload, ensure_ascii=True, indent=2)


def rank_semantic_candidates(
    query: str,
    candidates: Iterable[SemanticCandidate],
    *,
    top_k: int = 50,
    minimum_score: float | None = None,
    max_candidates: int | None = DEFAULT_SEMANTIC_RANKING_CANDIDATE_LIMIT,
    chat_runner: SemanticChatRunner | None = None,
) -> tuple[SemanticMatch, ...]:
    all_candidates = tuple(candidates)
    candidate_tuple = select_semantic_candidates_for_query(query, all_candidates, max_candidates=max_candidates)
    if not candidate_tuple:
        return ()

    if chat_runner is None:
        return rank_semantic_candidates_locally(
            query,
            all_candidates,
            top_k=top_k,
            minimum_score=minimum_score,
        )

    prompt = build_semantic_ranking_prompt(
        query,
        candidate_tuple,
        top_k=top_k,
        minimum_score=minimum_score,
    )
    resolved_chat_runner = chat_runner or run_local_semantic_chat
    response_text = resolved_chat_runner(prompt, SEMANTIC_RANKER_SYSTEM_PROMPT)
    return parse_semantic_match_response(
        response_text,
        build_semantic_candidate_map(candidate_tuple),
        top_k=top_k,
        minimum_score=minimum_score,
    )


def rank_student_rows_semantically(
    query: str,
    students: Iterable[StudentCurrent],
    *,
    source_fields: Iterable[str] | None = None,
    top_k: int = 50,
    minimum_score: float | None = None,
    max_candidates: int | None = DEFAULT_SEMANTIC_RANKING_CANDIDATE_LIMIT,
    chat_runner: SemanticChatRunner | None = None,
) -> tuple[SemanticMatch, ...]:
    candidates = build_semantic_candidates_from_students(students, source_fields=source_fields)
    return rank_semantic_candidates(
        query,
        candidates,
        top_k=top_k,
        minimum_score=minimum_score,
        max_candidates=max_candidates,
        chat_runner=chat_runner,
    )


def rank_semantic_candidates_locally(
    query: str,
    candidates: Iterable[SemanticCandidate],
    *,
    top_k: int = 50,
    minimum_score: float | None = None,
) -> tuple[SemanticMatch, ...]:
    if top_k <= 0:
        raise OllamaModelError("Semantic top_k must be positive.")
    validate_minimum_score(minimum_score)

    expanded_terms = expand_semantic_query_terms(query)
    query_phrases = semantic_query_phrases(query)
    if not expanded_terms and not query_phrases:
        raise OllamaModelError("Semantic query cannot be empty.")

    matches = []
    for candidate in candidates:
        score, reason = score_semantic_candidate(candidate, expanded_terms, query_phrases)
        if score <= 0:
            continue
        if minimum_score is not None and score < minimum_score:
            continue
        matches.append(
            SemanticMatch(
                STUD_ID=candidate.STUD_ID,
                score=score,
                reason=reason,
                document_hash=candidate.document_hash,
            )
        )

    return tuple(sorted(matches, key=lambda match: (-match.score, match.STUD_ID))[:top_k])


def select_semantic_candidates_for_query(
    query: str,
    candidates: Iterable[SemanticCandidate],
    *,
    max_candidates: int | None = DEFAULT_SEMANTIC_RANKING_CANDIDATE_LIMIT,
) -> tuple[SemanticCandidate, ...]:
    candidate_tuple = tuple(candidates)
    if max_candidates is None or len(candidate_tuple) <= max_candidates:
        return candidate_tuple
    if max_candidates <= 0:
        raise OllamaModelError("Semantic max_candidates must be positive.")

    query_tokens = semantic_query_tokens(query)
    if not query_tokens:
        return candidate_tuple[:max_candidates]

    scored_candidates = tuple(
        (
            semantic_candidate_lexical_score(query_tokens, candidate),
            index,
            candidate,
        )
        for index, candidate in enumerate(candidate_tuple)
    )
    return tuple(
        candidate
        for _score, _index, candidate in sorted(scored_candidates, key=lambda item: (-item[0], item[1]))[:max_candidates]
    )


def truncate_semantic_prompt_text(value: str, *, max_length: int = DEFAULT_SEMANTIC_PROMPT_TEXT_LIMIT) -> str:
    clean_value = clean_semantic_value(value)
    if len(clean_value) <= max_length:
        return clean_value
    return f"{clean_value[: max_length - 3].rstrip()}..."


def semantic_query_tokens(query: str) -> tuple[str, ...]:
    tokens: list[str] = []
    for token in SEMANTIC_TOKEN_RE.findall(clean_semantic_value(query).casefold()):
        normalized = normalize_semantic_token(token)
        if len(normalized) < 3 or normalized in SEMANTIC_QUERY_STOP_WORDS:
            continue
        if normalized not in tokens:
            tokens.append(normalized)
    return tuple(tokens)


def semantic_candidate_lexical_score(query_tokens: tuple[str, ...], candidate: SemanticCandidate) -> int:
    candidate_text = normalize_semantic_text(candidate.text)
    score = 0
    for token in query_tokens:
        occurrences = candidate_text.count(token)
        if occurrences:
            score += 3 + min(occurrences, 3)
    return score


def expand_semantic_query_terms(query: str) -> dict[str, float]:
    terms: dict[str, float] = {}
    for token in semantic_query_tokens(query):
        terms[token] = max(terms.get(token, 0), 1.0)
        for synonym in LOCAL_SEMANTIC_SYNONYMS.get(token, ()):
            normalized_synonym = normalize_semantic_token(synonym)
            if normalized_synonym and normalized_synonym not in SEMANTIC_QUERY_STOP_WORDS:
                terms[normalized_synonym] = max(terms.get(normalized_synonym, 0), 0.72)
    return terms


def semantic_query_phrases(query: str) -> tuple[str, ...]:
    tokens = semantic_query_tokens(query)
    phrases = []
    for index in range(len(tokens) - 1):
        phrase = f"{tokens[index]} {tokens[index + 1]}"
        if phrase not in phrases:
            phrases.append(phrase)
    return tuple(phrases)


def score_semantic_candidate(
    candidate: SemanticCandidate,
    expanded_terms: dict[str, float],
    query_phrases: tuple[str, ...],
) -> tuple[float, str]:
    field_scores: dict[str, float] = {}
    matched_terms_by_field: dict[str, set[str]] = {}

    fields = candidate.fields or (SemanticTextField("semantic_text", "Student profile", candidate.text),)
    for field in fields:
        normalized_text = normalize_semantic_text(field.value)
        field_tokens = set(semantic_query_tokens(normalized_text))
        field_weight = LOCAL_SEMANTIC_FIELD_WEIGHTS.get(field.field_name, 1.0)
        raw_score = 0.0

        for term, query_weight in expanded_terms.items():
            if term in field_tokens or term in normalized_text:
                raw_score += query_weight * field_weight
                matched_terms_by_field.setdefault(field.label, set()).add(term)

        for phrase in query_phrases:
            if phrase in normalized_text:
                raw_score += 1.25 * field_weight
                matched_terms_by_field.setdefault(field.label, set()).add(phrase)

        if raw_score:
            field_scores[field.label] = field_scores.get(field.label, 0.0) + raw_score

    raw_total = sum(field_scores.values())
    if raw_total <= 0:
        return 0.0, ""

    max_reasonable_score = max(1.0, (len(expanded_terms) * 1.8) + (len(query_phrases) * 1.1))
    score = round(min(raw_total / max_reasonable_score, 1.0), 6)
    return score, build_local_semantic_reason(field_scores, matched_terms_by_field)


def build_local_semantic_reason(field_scores: dict[str, float], matched_terms_by_field: dict[str, set[str]]) -> str:
    top_fields = sorted(field_scores.items(), key=lambda item: (-item[1], item[0]))[:2]
    field_labels = [label for label, _score in top_fields]
    matched_terms = []
    for label in field_labels:
        for term in sorted(matched_terms_by_field.get(label, ())):
            if term not in matched_terms:
                matched_terms.append(term)
    term_summary = ", ".join(matched_terms[:5])
    field_summary = ", ".join(field_labels)
    if term_summary:
        return f"Matched {term_summary} in {field_summary}"
    return f"Matched related profile text in {field_summary}"


def normalize_semantic_text(value: object) -> str:
    return " ".join(normalize_semantic_token(token) for token in SEMANTIC_TOKEN_RE.findall(clean_semantic_value(value)))


def normalize_semantic_token(value: object) -> str:
    token = clean_semantic_value(value).casefold()
    token = re.sub(r"[^a-z0-9]+", "", token)
    if len(token) > 5 and token.endswith("ing"):
        token = token[:-3]
    elif len(token) > 4 and token.endswith("ed"):
        token = token[:-2]
    elif len(token) > 4 and token.endswith("ies"):
        token = f"{token[:-3]}y"
    elif len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        token = token[:-1]
    return token


def parse_semantic_match_response(
    response_text: str,
    candidate_map: dict[str, SemanticCandidate],
    *,
    top_k: int,
    minimum_score: float | None = None,
) -> tuple[SemanticMatch, ...]:
    validate_minimum_score(minimum_score)
    if top_k <= 0:
        raise OllamaModelError("Semantic top_k must be positive.")

    try:
        payload = json.loads(extract_json_payload(response_text))
    except json.JSONDecodeError as exc:
        raise OllamaModelError(f"Could not parse semantic model JSON response: {exc}") from exc

    raw_matches = payload.get("matches", payload) if isinstance(payload, dict) else payload
    if not isinstance(raw_matches, list):
        raise OllamaModelError("Semantic model response must contain a matches list.")

    matches: list[SemanticMatch] = []
    seen_student_ids: set[str] = set()
    for raw_match in raw_matches:
        if not isinstance(raw_match, dict):
            continue
        student_id = clean_semantic_value(raw_match.get("STUD_ID") or raw_match.get("stud_id"))
        if not student_id or student_id in seen_student_ids or student_id not in candidate_map:
            continue

        score = parse_semantic_score(raw_match.get("score"))
        if score is None:
            continue
        if minimum_score is not None and score < minimum_score:
            continue

        candidate = candidate_map[student_id]
        matches.append(
            SemanticMatch(
                STUD_ID=student_id,
                score=score,
                reason=clean_semantic_value(raw_match.get("reason")),
                document_hash=candidate.document_hash,
            )
        )
        seen_student_ids.add(student_id)

    return tuple(sorted(matches, key=lambda match: (-match.score, match.STUD_ID))[:top_k])


def extract_json_payload(response_text: str) -> str:
    text = clean_semantic_value(response_text)
    if not text:
        raise OllamaModelError("Semantic model response was empty.")

    start_indexes = [index for index in (text.find("{"), text.find("[")) if index >= 0]
    if not start_indexes:
        raise OllamaModelError("Semantic model response did not contain JSON.")

    start = min(start_indexes)
    end = max(text.rfind("}"), text.rfind("]"))
    if end < start:
        raise OllamaModelError("Semantic model response JSON was incomplete.")
    return text[start : end + 1]


def parse_semantic_score(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        score = float(value)
    except (TypeError, ValueError):
        return None

    if 1.0 < score <= 100.0:
        score = score / 100.0
    if score < 0.0 or score > 1.0:
        return None
    return round(score, 6)


def validate_minimum_score(minimum_score: float | None) -> None:
    if minimum_score is None:
        return
    if isinstance(minimum_score, bool) or minimum_score < 0.0 or minimum_score > 1.0:
        raise OllamaModelError("Semantic minimum_score must be between 0 and 1.")


def default_semantic_field_names(student: StudentCurrent, include_extra_columns: bool) -> tuple[str, ...]:
    field_names = list(DEFAULT_SEMANTIC_TEXT_FIELDS)
    if include_extra_columns:
        field_names.extend(sorted(extra_text_column_names(student)))
    return tuple(dict.fromkeys(field_names))


def extra_text_column_names(student: StudentCurrent) -> tuple[str, ...]:
    extra_columns = student.extra_columns_json or {}
    return tuple(
        column_name
        for column_name, value in extra_columns.items()
        if clean_semantic_value(value) and not is_private_semantic_field(column_name)
    )


def read_student_value(student: StudentCurrent, field_name: str) -> Any:
    if hasattr(student, field_name):
        return getattr(student, field_name)
    return (student.extra_columns_json or {}).get(field_name)


def clean_semantic_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "Yes" if value else "No"
    return WHITESPACE_RE.sub(" ", str(value)).strip()


def format_semantic_fields(fields: Iterable[SemanticTextField]) -> str:
    return "\n".join(f"{field.label}: {field.value}" for field in fields)


def semantic_field_label(field_name: str) -> str:
    return FIELD_LABELS.get(field_name, humanize_field_name(field_name))


def humanize_field_name(field_name: str) -> str:
    clean_name = field_name
    if clean_name.startswith("WSP_"):
        clean_name = clean_name.removeprefix("WSP_")
    return clean_name.replace("_", " ").strip().title()


def is_private_semantic_field(field_name: str) -> bool:
    normalized = field_name.upper()
    return normalized in PRIVATE_SEMANTIC_TEXT_FIELDS or any(token in normalized for token in PRIVATE_FIELD_TOKENS)


def normalize_ollama_base_url(base_url: str) -> str:
    clean_url = base_url.strip().rstrip("/")
    if not clean_url:
        raise OllamaModelError("Ollama base URL cannot be empty.")
    return clean_url


def ollama_api_url(base_url: str, path: str) -> str:
    clean_path = path if path.startswith("/") else f"/{path}"
    return f"{normalize_ollama_base_url(base_url)}{clean_path}"


def http_get_json(url: str, timeout_seconds: float) -> dict[str, Any]:
    try:
        with request.urlopen(request.Request(url, method="GET"), timeout=timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))
    except (OSError, TimeoutError, json.JSONDecodeError) as exc:
        raise OllamaModelError(f"Ollama request failed for {url}: {exc}") from exc


def http_post_json(url: str, payload: dict[str, Any], timeout_seconds: float) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    http_request = request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(http_request, timeout=timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))
    except (OSError, TimeoutError, json.JSONDecodeError, error.HTTPError) as exc:
        raise OllamaModelError(f"Ollama request failed for {url}: {exc}") from exc


def check_semantic_model_status(
    settings: AppSettings,
    *,
    http_get: JsonGetter = http_get_json,
) -> OllamaModelStatus:
    if not settings.semantic_search_enabled:
        return OllamaModelStatus(
            enabled=False,
            base_url=normalize_ollama_base_url(settings.ollama_base_url),
            model_name=settings.ollama_model_name,
            server_available=False,
            model_available=False,
            error_message="Semantic search is disabled.",
        )

    return check_ollama_model_availability(
        base_url=settings.ollama_base_url,
        model_name=settings.ollama_model_name,
        timeout_seconds=settings.ollama_request_timeout_seconds,
        http_get=http_get,
    )


def check_ollama_model_availability(
    *,
    base_url: str = DEFAULT_OLLAMA_BASE_URL,
    model_name: str = DEFAULT_OLLAMA_MODEL_NAME,
    timeout_seconds: float = 5.0,
    http_get: JsonGetter = http_get_json,
) -> OllamaModelStatus:
    tags_url = ollama_api_url(base_url, "/api/tags")

    try:
        response = http_get(tags_url, timeout_seconds)
    except OllamaModelError as exc:
        return OllamaModelStatus(
            enabled=True,
            base_url=normalize_ollama_base_url(base_url),
            model_name=model_name,
            server_available=False,
            model_available=False,
            error_message=(
                f"Ollama is not reachable at {normalize_ollama_base_url(base_url)}. "
                f"Install/start Ollama, then run: ollama run {model_name}. Details: {exc}"
            ),
        )

    available_models = tuple(
        sorted(
            model["name"]
            for model in response.get("models", [])
            if isinstance(model, dict) and isinstance(model.get("name"), str)
        )
    )
    model_available = model_name in available_models
    error_message = None
    if not model_available:
        error_message = f"Ollama is running, but model {model_name!r} is not installed. Run: ollama run {model_name}."

    return OllamaModelStatus(
        enabled=True,
        base_url=normalize_ollama_base_url(base_url),
        model_name=model_name,
        server_available=True,
        model_available=model_available,
        available_models=available_models,
        error_message=error_message,
    )


def ensure_ollama_model_available(status: OllamaModelStatus) -> OllamaModelStatus:
    if not status.enabled:
        raise OllamaModelError("Semantic search is disabled in settings.")
    if not status.server_available or not status.model_available:
        raise OllamaModelError(status.error_message or f"Ollama model {status.model_name!r} is not available.")
    return status


def run_ollama_chat(
    prompt: str,
    *,
    base_url: str = DEFAULT_OLLAMA_BASE_URL,
    model_name: str = DEFAULT_OLLAMA_MODEL_NAME,
    system_prompt: str | None = None,
    timeout_seconds: float = DEFAULT_OLLAMA_TIMEOUT_SECONDS,
    response_format: str | dict[str, Any] | None = None,
    think: bool | str | None = False,
    options: dict[str, Any] | None = None,
    http_post: JsonPoster = http_post_json,
) -> str:
    clean_prompt = clean_semantic_value(prompt)
    if not clean_prompt:
        raise OllamaModelError("Ollama prompt cannot be empty.")

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": clean_semantic_value(system_prompt)})
    messages.append({"role": "user", "content": clean_prompt})

    payload: dict[str, Any] = {"model": model_name, "messages": messages, "stream": False}
    if response_format is not None:
        payload["format"] = response_format
    if think is not None:
        payload["think"] = think
    if options is not None:
        payload["options"] = options

    response = http_post(ollama_api_url(base_url, "/api/chat"), payload, timeout_seconds)
    content = clean_semantic_value(response.get("message", {}).get("content"))
    if not content:
        raise OllamaModelError("Ollama returned an empty chat response.")
    return content


def run_local_semantic_chat(prompt: str, system_prompt: str | None) -> str:
    return run_ollama_chat(
        prompt,
        system_prompt=system_prompt,
        timeout_seconds=DEFAULT_OLLAMA_TIMEOUT_SECONDS,
        response_format="json",
        options={"temperature": 0, "num_predict": 256},
    )
