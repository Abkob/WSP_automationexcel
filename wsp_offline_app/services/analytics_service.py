from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import re
from statistics import mean
from typing import Callable, Iterable

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from database.models import ImportBatch, StudentCurrent


@dataclass(frozen=True)
class DashboardMetrics:
    total_students: int
    new_students_latest_import: int
    updated_students_latest_import: int
    average_gpa: float | None
    probation_count: int
    dean_warning_count: int
    financial_aid_count: int
    dorm_count: int
    registered_count: int
    enrolled_count: int


@dataclass(frozen=True)
class ChartPoint:
    label: str
    value: int | float


@dataclass(frozen=True)
class DashboardCharts:
    students_by_major: tuple[ChartPoint, ...]
    students_by_class: tuple[ChartPoint, ...]
    gpa_distribution: tuple[ChartPoint, ...]
    average_gpa_by_major: tuple[ChartPoint, ...]
    probation_by_major: tuple[ChartPoint, ...]
    financial_aid_distribution: tuple[ChartPoint, ...]


@dataclass(frozen=True)
class LatestImportSummary:
    filename: str
    imported_at: str
    rows_added: int
    rows_updated: int
    rows_unchanged: int
    rows_missing: int
    new_columns: tuple[str, ...]
    missing_columns: tuple[str, ...]
    status: str
    error_message: str | None


@dataclass(frozen=True)
class TextFrequencyPoint:
    label: str
    value: int
    raw_terms: tuple[str, ...] = ()


@dataclass(frozen=True)
class TextAndSemanticAnalytics:
    preferred_work_distribution: tuple[TextFrequencyPoint, ...]
    technical_skills_frequency: tuple[TextFrequencyPoint, ...]
    languages_frequency: tuple[TextFrequencyPoint, ...]
    raw_source_text: dict[str, tuple[str, ...]]


GPA_BINS: tuple[tuple[str, float, float], ...] = (
    ("0.00-0.99", 0.0, 0.99),
    ("1.00-1.99", 1.0, 1.99),
    ("2.00-2.99", 2.0, 2.99),
    ("3.00-3.49", 3.0, 3.49),
    ("3.50-4.00", 3.5, 4.0),
)
TERM_SPLIT_RE = re.compile(r"[,;\n\r\t/|]+")
SKILL_LANGUAGE_SPLIT_RE = re.compile(r"[,;\n\r\t/|]+|\s+\band\b\s+", re.IGNORECASE)
WHITESPACE_RE = re.compile(r"\s+")
EDGE_PUNCTUATION_RE = re.compile(r"^[\s.:\-]+|[\s.:\-]+$")
TermClusterer = Callable[[str, str], str]

TERM_ALIASES = {
    "ms excel": "Excel",
    "microsoft excel": "Excel",
    "excel spreadsheet": "Excel",
    "excel spreadsheets": "Excel",
    "spreadsheet": "Spreadsheets",
    "spreadsheets": "Spreadsheets",
    "py": "Python",
    "python programming": "Python",
    "python coding": "Python",
    "sql": "SQL",
    "sql server": "SQL",
    "english language": "English",
    "arabic language": "Arabic",
    "french language": "French",
}
ACRONYM_TERMS = {
    "ai": "AI",
    "css": "CSS",
    "html": "HTML",
    "js": "JavaScript",
    "sql": "SQL",
    "ui": "UI",
    "ux": "UX",
}


def get_dashboard_metrics(session: Session, *, include_missing: bool = False) -> DashboardMetrics:
    student_query = session.query(StudentCurrent)
    if not include_missing:
        student_query = student_query.filter(StudentCurrent.missing_from_latest_import.is_(False))

    latest_batch = session.query(ImportBatch).order_by(ImportBatch.batch_id.desc()).first()
    average_gpa = student_query.with_entities(func.avg(StudentCurrent.CUM_GPA)).scalar()

    return DashboardMetrics(
        total_students=student_query.count(),
        new_students_latest_import=latest_batch.new_rows if latest_batch else 0,
        updated_students_latest_import=latest_batch.updated_rows if latest_batch else 0,
        average_gpa=float(average_gpa) if average_gpa is not None else None,
        probation_count=count_true(student_query, StudentCurrent.PROBATION.is_(True)),
        dean_warning_count=count_true(student_query, or_(StudentCurrent.DEANS_WARNING.is_(True), StudentCurrent.DEAN_WARN.is_(True))),
        financial_aid_count=count_true(student_query, StudentCurrent.FINANCIAL_AID.is_(True)),
        dorm_count=count_true(student_query, StudentCurrent.DORMS.is_(True)),
        registered_count=count_true(student_query, StudentCurrent.REGISTERED_IND.is_(True)),
        enrolled_count=count_true(student_query, StudentCurrent.ENROLLED_IND.is_(True)),
    )


def count_true(base_query, condition) -> int:
    return base_query.filter(condition).count()


def get_dashboard_charts(session: Session, *, include_missing: bool = False) -> DashboardCharts:
    students = get_chart_students(session, include_missing=include_missing)

    return DashboardCharts(
        students_by_major=count_category(students, "MAJR_DESC"),
        students_by_class=count_category(students, "CLAS_DESC"),
        gpa_distribution=build_gpa_distribution(students),
        average_gpa_by_major=average_number_by_category(students, category_field="MAJR_DESC", number_field="CUM_GPA"),
        probation_by_major=count_boolean_by_category(students, category_field="MAJR_DESC", boolean_field="PROBATION"),
        financial_aid_distribution=count_boolean_distribution(students, "FINANCIAL_AID"),
    )


def get_chart_students(session: Session, *, include_missing: bool = False) -> tuple[StudentCurrent, ...]:
    query = session.query(StudentCurrent)
    if not include_missing:
        query = query.filter(StudentCurrent.missing_from_latest_import.is_(False))
    return tuple(query.all())


def normalize_chart_label(value: object) -> str:
    if value is None:
        return "Unknown"
    text = str(value).strip()
    return text or "Unknown"


def sort_chart_points(points: Counter[str]) -> tuple[ChartPoint, ...]:
    return tuple(
        ChartPoint(label=label, value=count)
        for label, count in sorted(points.items(), key=lambda item: (-item[1], item[0]))
    )


def count_category(students: tuple[StudentCurrent, ...], field_name: str) -> tuple[ChartPoint, ...]:
    counts = Counter(normalize_chart_label(getattr(student, field_name)) for student in students)
    return sort_chart_points(counts)


def build_gpa_distribution(students: tuple[StudentCurrent, ...]) -> tuple[ChartPoint, ...]:
    counts = {label: 0 for label, _, _ in GPA_BINS}

    for student in students:
        if student.CUM_GPA is None:
            continue
        for label, minimum, maximum in GPA_BINS:
            if minimum <= student.CUM_GPA <= maximum:
                counts[label] += 1
                break

    return tuple(ChartPoint(label=label, value=counts[label]) for label, _, _ in GPA_BINS)


def average_number_by_category(
    students: tuple[StudentCurrent, ...],
    *,
    category_field: str,
    number_field: str,
) -> tuple[ChartPoint, ...]:
    grouped_values: dict[str, list[float]] = defaultdict(list)

    for student in students:
        value = getattr(student, number_field)
        if value is None:
            continue
        label = normalize_chart_label(getattr(student, category_field))
        grouped_values[label].append(float(value))

    return tuple(
        ChartPoint(label=label, value=round(mean(values), 2))
        for label, values in sorted(grouped_values.items(), key=lambda item: (-mean(item[1]), item[0]))
    )


def count_boolean_by_category(
    students: tuple[StudentCurrent, ...],
    *,
    category_field: str,
    boolean_field: str,
) -> tuple[ChartPoint, ...]:
    counts: Counter[str] = Counter()
    for student in students:
        if getattr(student, boolean_field) is True:
            counts[normalize_chart_label(getattr(student, category_field))] += 1
    return sort_chart_points(counts)


def count_boolean_distribution(students: tuple[StudentCurrent, ...], field_name: str) -> tuple[ChartPoint, ...]:
    counts = Counter()
    for student in students:
        value = getattr(student, field_name)
        if value is True:
            counts["Yes"] += 1
        elif value is False:
            counts["No"] += 1
        else:
            counts["Unknown"] += 1

    return tuple(
        ChartPoint(label=label, value=counts[label])
        for label in ("Yes", "No", "Unknown")
        if counts[label] > 0
    )


def get_latest_import_summary(session: Session) -> LatestImportSummary | None:
    latest_batch = session.query(ImportBatch).order_by(ImportBatch.batch_id.desc()).first()
    if latest_batch is None:
        return None

    return LatestImportSummary(
        filename=latest_batch.filename,
        imported_at=latest_batch.imported_at.isoformat(),
        rows_added=latest_batch.new_rows,
        rows_updated=latest_batch.updated_rows,
        rows_unchanged=latest_batch.unchanged_rows,
        rows_missing=latest_batch.missing_rows,
        new_columns=tuple(latest_batch.new_columns_detected or ()),
        missing_columns=tuple(latest_batch.missing_columns_detected or ()),
        status=latest_batch.status,
        error_message=latest_batch.error_message,
    )


def get_text_and_semantic_analytics(
    session: Session,
    *,
    include_missing: bool = False,
    term_clusterer: TermClusterer | None = None,
) -> TextAndSemanticAnalytics:
    students = get_chart_students(session, include_missing=include_missing)
    raw_source_text = collect_raw_source_text(students)

    return TextAndSemanticAnalytics(
        preferred_work_distribution=count_terms_for_students(
            students,
            category="preferred_work",
            field_names=("WSP_PREFERRED_TYPE_OF_WORK",),
            split_on_and=False,
            term_clusterer=term_clusterer,
        ),
        technical_skills_frequency=count_terms_for_students(
            students,
            category="technical_skills",
            field_names=("WSP_TECHNICAL_SKILLS",),
            split_on_and=True,
            term_clusterer=term_clusterer,
        ),
        languages_frequency=count_terms_for_students(
            students,
            category="languages",
            field_names=("WSP_WRITTEN_LANGUAGES", "WSP_SPOKEN_LANGUAGES"),
            split_on_and=True,
            term_clusterer=term_clusterer,
        ),
        raw_source_text=raw_source_text,
    )


def collect_raw_source_text(students: Iterable[StudentCurrent]) -> dict[str, tuple[str, ...]]:
    source_fields = (
        "WSP_PREFERRED_TYPE_OF_WORK",
        "WSP_TECHNICAL_SKILLS",
        "WSP_WRITTEN_LANGUAGES",
        "WSP_SPOKEN_LANGUAGES",
    )
    raw_values: dict[str, list[str]] = {field_name: [] for field_name in source_fields}
    for student in students:
        for field_name in source_fields:
            value = clean_text_value(getattr(student, field_name))
            if value:
                raw_values[field_name].append(value)
    return {field_name: tuple(values) for field_name, values in raw_values.items()}


def count_terms_for_students(
    students: Iterable[StudentCurrent],
    *,
    category: str,
    field_names: tuple[str, ...],
    split_on_and: bool,
    term_clusterer: TermClusterer | None = None,
) -> tuple[TextFrequencyPoint, ...]:
    counts: Counter[str] = Counter()
    raw_terms_by_label: dict[str, set[str]] = defaultdict(set)

    for student in students:
        student_terms: set[str] = set()
        for field_name in field_names:
            for raw_term in split_subjective_terms(getattr(student, field_name), split_on_and=split_on_and):
                normalized = normalize_subjective_term(raw_term)
                if not normalized:
                    continue
                label = term_clusterer(category, normalized) if term_clusterer else normalized
                label = normalize_subjective_term(label)
                if not label:
                    continue
                student_terms.add(label)
                raw_terms_by_label[label].add(clean_text_value(raw_term))

        for term in student_terms:
            counts[term] += 1

    return tuple(
        TextFrequencyPoint(
            label=label,
            value=count,
            raw_terms=tuple(sorted(raw_terms_by_label[label])),
        )
        for label, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    )


def split_subjective_terms(value: object, *, split_on_and: bool) -> tuple[str, ...]:
    text = clean_text_value(value)
    if not text:
        return ()

    splitter = SKILL_LANGUAGE_SPLIT_RE if split_on_and else TERM_SPLIT_RE
    return tuple(part for part in (clean_text_value(part) for part in splitter.split(text)) if part)


def normalize_subjective_term(value: object) -> str:
    text = clean_text_value(value)
    if not text:
        return ""
    text = text.replace("_", " ").replace("-", " ")
    text = EDGE_PUNCTUATION_RE.sub("", text)
    text = WHITESPACE_RE.sub(" ", text).strip()
    if not text:
        return ""

    alias_key = text.casefold()
    if alias_key in TERM_ALIASES:
        return TERM_ALIASES[alias_key]

    return title_preserving_acronyms(text)


def clean_text_value(value: object) -> str:
    if value is None:
        return ""
    return WHITESPACE_RE.sub(" ", str(value)).strip()


def title_preserving_acronyms(value: str) -> str:
    words = []
    for word in value.split(" "):
        key = word.casefold()
        words.append(ACRONYM_TERMS.get(key, word.title()))
    return " ".join(words)
