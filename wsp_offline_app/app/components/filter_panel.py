from __future__ import annotations

from dataclasses import dataclass

from services.filter_service import (
    BooleanFilter,
    CategoryFilter,
    FilterRequest,
    NumericFilter,
    PaginationSpec,
    SemanticFilter,
    SortSpec,
    TextFilter,
)


BOOLEAN_SELECT_OPTIONS = {
    "any": "Any",
    "yes": "Yes",
    "no": "No",
}
SORT_FIELD_OPTIONS = {
    "STUD_ID": "Student ID",
    "STUD_NAME": "Name",
    "CUM_GPA": "GPA",
    "MAJR_DESC": "Major",
    "CLAS_DESC": "Class",
}
SORT_DIRECTION_OPTIONS = {
    "asc": "Ascending",
    "desc": "Descending",
}
PAGE_SIZE_OPTIONS = [25, 50, 100, 250]
DEFAULT_SELECTED_COLUMNS = (
    "STUD_ID",
    "STUD_NAME",
    "MAJR_DESC",
    "CLAS_DESC",
    "STUD_EMAIL",
    "CUM_GPA",
    "PROBATION",
    "FINANCIAL_AID",
    "DORMS",
    "WSP_TECHNICAL_SKILLS",
    "WSP_PREFERRED_TYPE_OF_WORK",
)


@dataclass(frozen=True)
class FilterOptionSet:
    majors: tuple[str, ...] = ()
    classes: tuple[str, ...] = ()


@dataclass(frozen=True)
class FilterUiState:
    name_query: str = ""
    technical_skills_query: str = ""
    semantic_query: str = ""
    gpa_min: float | None = None
    gpa_max: float | None = None
    major: str | None = None
    class_desc: str | None = None
    probation: str = "any"
    financial_aid: str = "any"
    dorms: str = "any"
    include_missing: bool = False
    sort_field: str = "STUD_ID"
    sort_direction: str = "asc"
    page_size: int = 50


def build_filter_request_from_state(state: FilterUiState) -> FilterRequest:
    numeric_filters = build_gpa_filters(state.gpa_min, state.gpa_max)
    boolean_filters = tuple(
        filter_item
        for filter_item in (
            build_boolean_filter("PROBATION", state.probation),
            build_boolean_filter("FINANCIAL_AID", state.financial_aid),
            build_boolean_filter("DORMS", state.dorms),
        )
        if filter_item is not None
    )
    category_filters = tuple(
        filter_item
        for filter_item in (
            build_category_filter("MAJR_DESC", state.major),
            build_category_filter("CLAS_DESC", state.class_desc),
        )
        if filter_item is not None
    )
    text_filters = tuple(
        filter_item
        for filter_item in (
            build_text_filter("STUD_NAME", state.name_query),
            build_text_filter("WSP_TECHNICAL_SKILLS", state.technical_skills_query),
        )
        if filter_item is not None
    )
    semantic_filter = build_semantic_filter(state.semantic_query)

    return FilterRequest(
        numeric_filters=numeric_filters,
        boolean_filters=boolean_filters,
        category_filters=category_filters,
        text_filters=text_filters,
        semantic_filter=semantic_filter,
        sort=SortSpec(state.sort_field, state.sort_direction),
        pagination=PaginationSpec(page=1, page_size=int(state.page_size)),
        include_missing=state.include_missing,
        selected_columns=DEFAULT_SELECTED_COLUMNS,
    )


def build_gpa_filters(gpa_min: float | None, gpa_max: float | None) -> tuple[NumericFilter, ...]:
    if gpa_min is None and gpa_max is None:
        return ()
    if gpa_min is not None and gpa_max is not None:
        lower, upper = sorted((float(gpa_min), float(gpa_max)))
        return (NumericFilter("CUM_GPA", "between", lower, upper),)
    if gpa_min is not None:
        return (NumericFilter("CUM_GPA", ">=", float(gpa_min)),)
    return (NumericFilter("CUM_GPA", "<=", float(gpa_max)),)


def build_boolean_filter(field_name: str, selected_value: str) -> BooleanFilter | None:
    resolved_value = resolve_boolean_selection(selected_value)
    if resolved_value is None:
        return None
    return BooleanFilter(field_name, resolved_value)


def resolve_boolean_selection(selected_value: str) -> bool | None:
    if selected_value == "yes":
        return True
    if selected_value == "no":
        return False
    return None


def build_category_filter(field_name: str, value: str | None) -> CategoryFilter | None:
    clean_value = clean_text_filter_value(value)
    if clean_value is None:
        return None
    return CategoryFilter(field_name, (clean_value,))


def build_text_filter(field_name: str, value: str | None) -> TextFilter | None:
    clean_value = clean_text_filter_value(value)
    if clean_value is None:
        return None
    return TextFilter(field_name, "contains", clean_value)


def build_semantic_filter(value: str | None) -> SemanticFilter | None:
    clean_value = clean_text_filter_value(value)
    if clean_value is None:
        return None
    return SemanticFilter(clean_value, top_k=50, minimum_score=0.1)


def clean_text_filter_value(value: str | None) -> str | None:
    if value is None:
        return None
    clean_value = " ".join(str(value).strip().split())
    return clean_value or None


def build_result_summary(total_count: int, visible_count: int, applied_filter_count: int) -> str:
    filter_label = "filter" if applied_filter_count == 1 else "filters"
    result_label = "result" if total_count == 1 else "results"
    return f"{total_count:,} {result_label} - {visible_count:,} visible - {applied_filter_count} {filter_label}"
