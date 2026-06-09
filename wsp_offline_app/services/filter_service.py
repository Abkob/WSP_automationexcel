from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Iterable

from sqlalchemy import and_, asc, desc, or_
from sqlalchemy.orm import Session

from database.models import ExportLog, FilterPreset, FilterRun, StudentCurrent
from services.semantic_service import SemanticMatch, rank_student_rows_semantically


class FilterValidationError(ValueError):
    """Raised when a filter request contains an invalid field or operator."""


class FilterPresetError(ValueError):
    """Raised when filter preset operations fail."""


NUMERIC_FILTER_FIELDS = {"CUM_GPA", "TOTAL_CREDIT_HOURS", "ENRL_TERM", "ASTD_TERM"}
BOOLEAN_FILTER_FIELDS = {
    "PROBATION",
    "DEANS_WARNING",
    "DEAN_WARN",
    "ENROLLED_IND",
    "REGISTERED_IND",
    "USAID",
    "MASTER_CARD",
    "UPP_MEPI",
    "GAS",
    "FINANCIAL_AID",
    "DORMS",
}
CATEGORY_FILTER_FIELDS = {
    "MAJR_DESC",
    "CLAS_DESC",
    "STST_DESC",
    "STYP_CODE",
    "STYP_DESC",
    "LEVL_CODE",
    "COLL_CODE",
    "ASTD_DESC",
}
TEXT_FILTER_FIELDS = {
    "STUD_ID",
    "STUD_NAME",
    "STUD_EMAIL",
    "WSP_WRITTEN_LANGUAGES",
    "WSP_SPOKEN_LANGUAGES",
    "WSP_ORGANIZATIONAL_SKILLS",
    "WSP_TECHNICAL_SKILLS",
    "WSP_INTERPERSONAL_SKILLS",
    "WSP_ADDITIONAL_SKILLS",
    "WSP_PREV_WORK",
    "WSP_PREVIOUS_TYPE_OF_WORK",
    "WSP_PREFERRED_TYPE_OF_WORK",
}
SEMANTIC_FILTER_FIELDS = {
    "WSP_WRITTEN_LANGUAGES",
    "WSP_SPOKEN_LANGUAGES",
    "WSP_ORGANIZATIONAL_SKILLS",
    "WSP_TECHNICAL_SKILLS",
    "WSP_INTERPERSONAL_SKILLS",
    "WSP_ADDITIONAL_SKILLS",
    "WSP_PREVIOUS_TYPE_OF_WORK",
    "WSP_PREFERRED_TYPE_OF_WORK",
}

NUMERIC_OPERATORS = {"=", ">", ">=", "<", "<=", "between", "is empty", "is not empty"}
TEXT_OPERATORS = {"contains", "does not contain", "starts with", "ends with", "exact match", "is empty", "is not empty"}
SORT_DIRECTIONS = {"asc", "desc"}
ALL_FILTER_FIELDS = (
    NUMERIC_FILTER_FIELDS
    | BOOLEAN_FILTER_FIELDS
    | CATEGORY_FILTER_FIELDS
    | TEXT_FILTER_FIELDS
)
AUDIT_RESULT_FIELDS = {"created_at", "updated_at", "added_to_db_at", "modified_in_db_at"}

GLOBAL_SEARCH_COLUMNS = (
    "STUD_ID",
    "STUD_NAME",
    "STUD_EMAIL",
    "MAJR_DESC",
    "CLAS_DESC",
    "WSP_TECHNICAL_SKILLS",
    "WSP_PREFERRED_TYPE_OF_WORK",
    "WSP_ORGANIZATIONAL_SKILLS",
    "WSP_ADDITIONAL_SKILLS",
    "WSP_SPOKEN_LANGUAGES",
    "WSP_WRITTEN_LANGUAGES",
    "WSP_INTERPERSONAL_SKILLS",
)


@dataclass(frozen=True)
class NumericFilter:
    field_name: str
    operator: str
    value: float | int | None = None
    value_to: float | int | None = None

    def __post_init__(self) -> None:
        validate_field(self.field_name, NUMERIC_FILTER_FIELDS)
        validate_operator(self.operator, NUMERIC_OPERATORS)

        if self.operator == "between" and (self.value is None or self.value_to is None):
            raise FilterValidationError("Numeric 'between' filter requires value and value_to")
        if self.operator not in {"between", "is empty", "is not empty"} and self.value is None:
            raise FilterValidationError(f"Numeric operator {self.operator!r} requires value")
        if self.operator == "between":
            validate_numeric_input(self.value, "value")
            validate_numeric_input(self.value_to, "value_to")
        elif self.operator not in {"is empty", "is not empty"}:
            validate_numeric_input(self.value, "value")


@dataclass(frozen=True)
class BooleanFilter:
    field_name: str
    value: bool | None

    def __post_init__(self) -> None:
        validate_field(self.field_name, BOOLEAN_FILTER_FIELDS)


@dataclass(frozen=True)
class CategoryFilter:
    field_name: str
    values: tuple[str | None, ...]

    def __post_init__(self) -> None:
        validate_field(self.field_name, CATEGORY_FILTER_FIELDS)
        object.__setattr__(self, "values", tuple(self.values))
        if not self.values:
            raise FilterValidationError("Category filter requires at least one value")


@dataclass(frozen=True)
class TextFilter:
    field_name: str
    operator: str
    value: str | None = None

    def __post_init__(self) -> None:
        validate_field(self.field_name, TEXT_FILTER_FIELDS)
        validate_operator(self.operator, TEXT_OPERATORS)
        if self.operator not in {"is empty", "is not empty"} and not self.value:
            raise FilterValidationError(f"Text operator {self.operator!r} requires value")


@dataclass(frozen=True)
class SemanticFilter:
    query: str
    source_fields: tuple[str, ...] = field(default_factory=lambda: tuple(sorted(SEMANTIC_FILTER_FIELDS)))
    top_k: int = 50
    minimum_score: float | None = None

    def __post_init__(self) -> None:
        if not self.query.strip():
            raise FilterValidationError("Semantic query cannot be empty")
        if self.top_k <= 0:
            raise FilterValidationError("Semantic top_k must be positive")
        for field_name in self.source_fields:
            validate_field(field_name, SEMANTIC_FILTER_FIELDS)


SemanticRanker = Callable[[SemanticFilter, tuple[StudentCurrent, ...]], tuple[SemanticMatch, ...]]


@dataclass(frozen=True)
class SortSpec:
    field_name: str
    direction: str = "asc"

    def __post_init__(self) -> None:
        validate_field(self.field_name, ALL_FILTER_FIELDS | AUDIT_RESULT_FIELDS)
        validate_operator(self.direction, SORT_DIRECTIONS)


@dataclass(frozen=True)
class PaginationSpec:
    page: int = 1
    page_size: int = 50

    def __post_init__(self) -> None:
        if self.page < 1:
            raise FilterValidationError("Pagination page must be 1 or greater")
        if self.page_size < 1 or self.page_size > 500:
            raise FilterValidationError("Pagination page_size must be between 1 and 500")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


@dataclass(frozen=True)
class FilterRequest:
    numeric_filters: tuple[NumericFilter, ...] = ()
    boolean_filters: tuple[BooleanFilter, ...] = ()
    category_filters: tuple[CategoryFilter, ...] = ()
    text_filters: tuple[TextFilter, ...] = ()
    semantic_filter: SemanticFilter | None = None
    global_query: str | None = None
    sort: SortSpec | None = None
    pagination: PaginationSpec = field(default_factory=PaginationSpec)
    include_missing: bool = False
    selected_columns: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "numeric_filters", tuple(self.numeric_filters))
        object.__setattr__(self, "boolean_filters", tuple(self.boolean_filters))
        object.__setattr__(self, "category_filters", tuple(self.category_filters))
        object.__setattr__(self, "text_filters", tuple(self.text_filters))
        object.__setattr__(self, "selected_columns", tuple(self.selected_columns))

        for column_name in self.selected_columns:
            validate_field(column_name, ALL_FILTER_FIELDS | AUDIT_RESULT_FIELDS | {"internal_id", "missing_from_latest_import"})


@dataclass(frozen=True)
class FilterResult:
    rows: tuple[StudentCurrent, ...]
    selected_rows: tuple[dict[str, Any], ...]
    total_count: int
    page: int
    page_size: int
    applied_filter_count: int
    applied_filter_metadata: dict[str, Any]
    semantic_scores: dict[str, float] = field(default_factory=dict)
    semantic_reasons: dict[str, str] = field(default_factory=dict)


def validate_field(field_name: str, allowed_fields: Iterable[str]) -> None:
    if field_name not in set(allowed_fields):
        raise FilterValidationError(f"Invalid filter field: {field_name}")


def validate_operator(operator: str, allowed_operators: Iterable[str]) -> None:
    if operator not in set(allowed_operators):
        raise FilterValidationError(f"Invalid filter operator: {operator}")


def validate_numeric_input(value: object, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise FilterValidationError(f"Numeric {label} must be an int or float")


def execute_filter_request(
    session: Session,
    request: FilterRequest,
    *,
    semantic_ranker: SemanticRanker | None = None,
) -> FilterResult:
    query = session.query(StudentCurrent)

    if not request.include_missing:
        query = query.filter(StudentCurrent.missing_from_latest_import.is_(False))

    for numeric_filter in request.numeric_filters:
        query = apply_numeric_filter(query, numeric_filter)

    for boolean_filter in request.boolean_filters:
        query = apply_boolean_filter(query, boolean_filter)

    for category_filter in request.category_filters:
        query = apply_category_filter(query, category_filter)

    for text_filter in request.text_filters:
        query = apply_text_filter(query, text_filter)

    if request.global_query:
        query = apply_global_search(query, request.global_query)

    if request.semantic_filter is not None:
        return execute_semantic_filter_request(
            query,
            request,
            semantic_ranker=semantic_ranker,
        )

    total_count = query.count()

    if request.sort is not None:
        sort_column = getattr(StudentCurrent, request.sort.field_name)
        query = query.order_by(desc(sort_column) if request.sort.direction == "desc" else asc(sort_column))
    else:
        query = query.order_by(asc(StudentCurrent.STUD_ID))

    rows = tuple(
        query.offset(request.pagination.offset)
        .limit(request.pagination.page_size)
        .all()
    )
    selected_rows = serialize_selected_rows(rows, request.selected_columns)

    return FilterResult(
        rows=rows,
        selected_rows=selected_rows,
        total_count=total_count,
        page=request.pagination.page,
        page_size=request.pagination.page_size,
        applied_filter_count=count_applied_filters(request),
        applied_filter_metadata=build_filter_metadata(request),
    )


def execute_semantic_filter_request(
    query: Any,
    request: FilterRequest,
    *,
    semantic_ranker: SemanticRanker | None,
) -> FilterResult:
    if semantic_ranker is None:
        semantic_ranker = default_semantic_ranker

    candidate_rows = tuple(query.order_by(asc(StudentCurrent.STUD_ID)).all())
    matches = semantic_ranker(request.semantic_filter, candidate_rows) if request.semantic_filter else ()
    rows_by_id = {student.STUD_ID: student for student in candidate_rows}
    ranked_rows = tuple(rows_by_id[match.STUD_ID] for match in matches if match.STUD_ID in rows_by_id)
    semantic_scores = {match.STUD_ID: match.score for match in matches}
    semantic_reasons = {match.STUD_ID: match.reason for match in matches if match.reason}
    paged_rows = ranked_rows[request.pagination.offset : request.pagination.offset + request.pagination.page_size]
    selected_rows = serialize_selected_rows(
        paged_rows,
        request.selected_columns,
        semantic_scores=semantic_scores,
        semantic_reasons=semantic_reasons,
    )

    return FilterResult(
        rows=paged_rows,
        selected_rows=selected_rows,
        total_count=len(ranked_rows),
        page=request.pagination.page,
        page_size=request.pagination.page_size,
        applied_filter_count=count_applied_filters(request),
        applied_filter_metadata=build_filter_metadata(request) | {"semantic_result_count": len(ranked_rows)},
        semantic_scores=semantic_scores,
        semantic_reasons=semantic_reasons,
    )


def default_semantic_ranker(semantic_filter: SemanticFilter, candidate_rows: tuple[StudentCurrent, ...]) -> tuple[SemanticMatch, ...]:
    return rank_student_rows_semantically(
        semantic_filter.query,
        candidate_rows,
        source_fields=semantic_filter.source_fields,
        top_k=semantic_filter.top_k,
        minimum_score=semantic_filter.minimum_score,
    )


def apply_global_search(query, text: str):
    pattern = f"%{text.strip()}%"
    conditions = [
        getattr(StudentCurrent, col).ilike(pattern)
        for col in GLOBAL_SEARCH_COLUMNS
        if hasattr(StudentCurrent, col)
    ]
    return query.filter(or_(*conditions)) if conditions else query


def count_applied_filters(request: FilterRequest) -> int:
    return (
        len(request.numeric_filters)
        + len(request.boolean_filters)
        + len(request.category_filters)
        + len(request.text_filters)
        + (1 if request.semantic_filter is not None else 0)
        + (1 if request.global_query else 0)
    )


def serialize_selected_rows(
    rows: tuple[StudentCurrent, ...],
    selected_columns: tuple[str, ...],
    *,
    semantic_scores: dict[str, float] | None = None,
    semantic_reasons: dict[str, str] | None = None,
) -> tuple[dict[str, Any], ...]:
    if not selected_columns:
        return ()
    output_columns = selected_columns
    if semantic_scores and "semantic_score" not in output_columns:
        output_columns = selected_columns + ("semantic_score",)
    if semantic_reasons and "semantic_explanation" not in output_columns:
        output_columns = output_columns + ("semantic_explanation",)

    return tuple(
        {
            column_name: (
                semantic_scores.get(row.STUD_ID)
                if column_name == "semantic_score" and semantic_scores is not None
                else semantic_reasons.get(row.STUD_ID)
                if column_name == "semantic_explanation" and semantic_reasons is not None
                else getattr(row, column_name)
            )
            for column_name in output_columns
        }
        for row in rows
    )


def build_filter_metadata(request: FilterRequest) -> dict[str, Any]:
    return {
        "numeric_filters": [asdict(item) for item in request.numeric_filters],
        "boolean_filters": [asdict(item) for item in request.boolean_filters],
        "category_filters": [asdict(item) for item in request.category_filters],
        "text_filters": [asdict(item) for item in request.text_filters],
        "semantic_filter": asdict(request.semantic_filter) if request.semantic_filter else None,
        "global_query": request.global_query,
        "sort": asdict(request.sort) if request.sort else None,
        "pagination": asdict(request.pagination),
        "include_missing": request.include_missing,
        "selected_columns": request.selected_columns,
    }


def filter_request_to_json(request: FilterRequest) -> dict[str, Any]:
    return build_filter_metadata(request)


def filter_request_from_json(data: dict[str, Any]) -> FilterRequest:
    return FilterRequest(
        numeric_filters=tuple(NumericFilter(**item) for item in data.get("numeric_filters", [])),
        boolean_filters=tuple(BooleanFilter(**item) for item in data.get("boolean_filters", [])),
        category_filters=tuple(
            CategoryFilter(field_name=item["field_name"], values=tuple(item["values"]))
            for item in data.get("category_filters", [])
        ),
        text_filters=tuple(TextFilter(**item) for item in data.get("text_filters", [])),
        semantic_filter=(
            SemanticFilter(
                query=data["semantic_filter"]["query"],
                source_fields=tuple(data["semantic_filter"].get("source_fields", tuple(sorted(SEMANTIC_FILTER_FIELDS)))),
                top_k=data["semantic_filter"].get("top_k", 50),
                minimum_score=data["semantic_filter"].get("minimum_score"),
            )
            if data.get("semantic_filter")
            else None
        ),
        sort=SortSpec(**data["sort"]) if data.get("sort") else None,
        pagination=PaginationSpec(**data.get("pagination", {})),
        include_missing=data.get("include_missing", False),
        selected_columns=tuple(data.get("selected_columns", ())),
    )


def save_filter_preset(session: Session, preset_name: str, request: FilterRequest) -> FilterPreset:
    clean_name = preset_name.strip()
    if not clean_name:
        raise FilterPresetError("Preset name cannot be empty")
    if session.query(FilterPreset).filter_by(preset_name=clean_name).one_or_none() is not None:
        raise FilterPresetError(f"Filter preset already exists: {clean_name}")

    preset = FilterPreset(preset_name=clean_name, filter_json=filter_request_to_json(request))
    session.add(preset)
    session.flush()
    return preset


def load_filter_preset(session: Session, preset_name: str) -> FilterRequest:
    preset = session.query(FilterPreset).filter_by(preset_name=preset_name).one_or_none()
    if preset is None:
        raise FilterPresetError(f"Filter preset was not found: {preset_name}")
    return filter_request_from_json(preset.filter_json)


def rename_filter_preset(session: Session, preset_id: int, new_name: str) -> FilterPreset:
    clean_name = new_name.strip()
    if not clean_name:
        raise FilterPresetError("Preset name cannot be empty")

    preset = session.get(FilterPreset, preset_id)
    if preset is None:
        raise FilterPresetError(f"Filter preset was not found: {preset_id}")

    existing = session.query(FilterPreset).filter_by(preset_name=clean_name).one_or_none()
    if existing is not None and existing.preset_id != preset_id:
        raise FilterPresetError(f"Filter preset already exists: {clean_name}")

    preset.preset_name = clean_name
    session.flush()
    return preset


def delete_filter_preset(session: Session, preset_id: int) -> None:
    preset = session.get(FilterPreset, preset_id)
    if preset is None:
        raise FilterPresetError(f"Filter preset was not found: {preset_id}")
    session.delete(preset)
    session.flush()


def log_filter_run(
    session: Session,
    *,
    request: FilterRequest,
    result_count: int,
    preset_id: int | None = None,
) -> FilterRun:
    filter_run = FilterRun(
        preset_id=preset_id,
        filter_json=filter_request_to_json(request),
        result_count=result_count,
    )
    session.add(filter_run)
    session.flush()
    return filter_run


def log_filter_export(
    session: Session,
    *,
    filter_run_id: int,
    export_path: str,
    row_count: int,
) -> ExportLog:
    if session.get(FilterRun, filter_run_id) is None:
        raise FilterPresetError(f"Filter run was not found: {filter_run_id}")

    export_log = ExportLog(
        filter_run_id=filter_run_id,
        export_path=export_path,
        row_count=row_count,
    )
    session.add(export_log)
    session.flush()
    return export_log


def apply_numeric_filter(query: Any, numeric_filter: NumericFilter) -> Any:
    column = getattr(StudentCurrent, numeric_filter.field_name)
    operator = numeric_filter.operator

    if operator == "=":
        return query.filter(column == numeric_filter.value)
    if operator == ">":
        return query.filter(column > numeric_filter.value)
    if operator == ">=":
        return query.filter(column >= numeric_filter.value)
    if operator == "<":
        return query.filter(column < numeric_filter.value)
    if operator == "<=":
        return query.filter(column <= numeric_filter.value)
    if operator == "between":
        return query.filter(column >= numeric_filter.value, column <= numeric_filter.value_to)
    if operator == "is empty":
        return query.filter(column.is_(None))
    if operator == "is not empty":
        return query.filter(column.is_not(None))

    raise FilterValidationError(f"Invalid filter operator: {operator}")


def apply_boolean_filter(query: Any, boolean_filter: BooleanFilter) -> Any:
    if boolean_filter.value is None:
        return query

    column = getattr(StudentCurrent, boolean_filter.field_name)
    return query.filter(column.is_(boolean_filter.value))


def apply_category_filter(query: Any, category_filter: CategoryFilter) -> Any:
    column = getattr(StudentCurrent, category_filter.field_name)
    non_null_values = [value for value in category_filter.values if value is not None]
    include_null = any(value is None for value in category_filter.values)

    conditions = []
    if non_null_values:
        conditions.append(column.in_(non_null_values))
    if include_null:
        conditions.append(column.is_(None))

    return query.filter(or_(*conditions))


def escape_like_text(value: str, escape_char: str = "\\") -> str:
    return (
        value.replace(escape_char, escape_char + escape_char)
        .replace("%", escape_char + "%")
        .replace("_", escape_char + "_")
    )


def apply_text_filter(query: Any, text_filter: TextFilter) -> Any:
    column = getattr(StudentCurrent, text_filter.field_name)
    operator = text_filter.operator

    if operator == "is empty":
        return query.filter(or_(column.is_(None), column == ""))
    if operator == "is not empty":
        return query.filter(and_(column.is_not(None), column != ""))

    escaped_value = escape_like_text(text_filter.value or "")
    if operator == "contains":
        return query.filter(column.ilike(f"%{escaped_value}%", escape="\\"))
    if operator == "does not contain":
        return query.filter(or_(column.is_(None), column.notilike(f"%{escaped_value}%", escape="\\")))
    if operator == "starts with":
        return query.filter(column.ilike(f"{escaped_value}%", escape="\\"))
    if operator == "ends with":
        return query.filter(column.ilike(f"%{escaped_value}", escape="\\"))
    if operator == "exact match":
        return query.filter(column.ilike(escaped_value, escape="\\"))

    raise FilterValidationError(f"Invalid filter operator: {operator}")
