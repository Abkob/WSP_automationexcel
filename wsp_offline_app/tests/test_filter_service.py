from __future__ import annotations

import pytest

from database.db import create_session_factory, create_sqlite_engine, initialize_database
from database.models import ExportLog, FilterPreset, FilterRun, StudentCurrent
from services.semantic_service import SemanticMatch
from services.filter_service import (
    BooleanFilter,
    CategoryFilter,
    FilterPresetError,
    FilterRequest,
    FilterValidationError,
    NumericFilter,
    PaginationSpec,
    SemanticFilter,
    SortSpec,
    TextFilter,
    count_applied_filters,
    delete_filter_preset,
    execute_filter_request,
    filter_request_from_json,
    filter_request_to_json,
    log_filter_export,
    log_filter_run,
    load_filter_preset,
    rename_filter_preset,
    save_filter_preset,
)


def test_valid_filter_request_parses() -> None:
    request = FilterRequest(
        numeric_filters=(NumericFilter("CUM_GPA", ">=", 3.0),),
        boolean_filters=(BooleanFilter("PROBATION", False),),
        category_filters=(CategoryFilter("MAJR_DESC", ("Computer Science",)),),
        text_filters=(TextFilter("WSP_TECHNICAL_SKILLS", "contains", "Python"),),
        semantic_filter=SemanticFilter("good at data analysis"),
        sort=SortSpec("CUM_GPA", "desc"),
        pagination=PaginationSpec(page=2, page_size=25),
        selected_columns=("STUD_ID", "STUD_NAME", "CUM_GPA"),
    )

    assert request.pagination.offset == 25
    assert count_applied_filters(request) == 5


def test_invalid_numeric_field_name_is_rejected() -> None:
    with pytest.raises(FilterValidationError, match="Invalid filter field"):
        NumericFilter("NOT_A_FIELD", ">=", 3.0)


def test_invalid_operator_is_rejected() -> None:
    with pytest.raises(FilterValidationError, match="Invalid filter operator"):
        NumericFilter("CUM_GPA", "approximately", 3.0)


def test_invalid_numeric_input_is_rejected() -> None:
    with pytest.raises(FilterValidationError, match="must be an int or float"):
        NumericFilter("CUM_GPA", ">=", "not a number")  # type: ignore[arg-type]

    with pytest.raises(FilterValidationError, match="must be an int or float"):
        NumericFilter("CUM_GPA", "=", True)  # type: ignore[arg-type]


def test_numeric_between_requires_two_values() -> None:
    with pytest.raises(FilterValidationError, match="between"):
        NumericFilter("CUM_GPA", "between", 2.0)


def test_text_filter_requires_value_for_matching_operator() -> None:
    with pytest.raises(FilterValidationError, match="requires value"):
        TextFilter("STUD_NAME", "contains", "")


def test_category_filter_requires_values() -> None:
    with pytest.raises(FilterValidationError, match="at least one value"):
        CategoryFilter("MAJR_DESC", ())


def test_semantic_filter_rejects_empty_query() -> None:
    with pytest.raises(FilterValidationError, match="cannot be empty"):
        SemanticFilter("   ")


def test_sort_and_pagination_validation() -> None:
    with pytest.raises(FilterValidationError, match="Invalid filter field"):
        SortSpec("NOT_A_FIELD")

    with pytest.raises(FilterValidationError, match="Invalid filter operator"):
        SortSpec("CUM_GPA", "sideways")

    with pytest.raises(FilterValidationError, match="page must be"):
        PaginationSpec(page=0)

    with pytest.raises(FilterValidationError, match="page_size"):
        PaginationSpec(page_size=501)


def test_empty_filter_returns_all_non_missing_current_students(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add_all(
            [
                StudentCurrent(STUD_ID="1001", STUD_NAME="Active One"),
                StudentCurrent(STUD_ID="1002", STUD_NAME="Active Two"),
                StudentCurrent(STUD_ID="1003", STUD_NAME="Missing", missing_from_latest_import=True),
            ]
        )
        session.commit()

    with session_factory() as session:
        result = execute_filter_request(session, FilterRequest())

    assert result.total_count == 2
    assert [student.STUD_ID for student in result.rows] == ["1001", "1002"]
    assert result.applied_filter_count == 0


def test_empty_filter_can_include_missing_students_when_requested(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add_all(
            [
                StudentCurrent(STUD_ID="1001", STUD_NAME="Active"),
                StudentCurrent(STUD_ID="1002", STUD_NAME="Missing", missing_from_latest_import=True),
            ]
        )
        session.commit()

    with session_factory() as session:
        result = execute_filter_request(session, FilterRequest(include_missing=True))

    assert result.total_count == 2
    assert [student.STUD_ID for student in result.rows] == ["1001", "1002"]


def test_empty_filter_supports_sorting_and_pagination(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add_all(
            [
                StudentCurrent(STUD_ID="1001", STUD_NAME="A", CUM_GPA=3.0),
                StudentCurrent(STUD_ID="1002", STUD_NAME="B", CUM_GPA=4.0),
                StudentCurrent(STUD_ID="1003", STUD_NAME="C", CUM_GPA=2.0),
            ]
        )
        session.commit()

    with session_factory() as session:
        result = execute_filter_request(
            session,
            FilterRequest(sort=SortSpec("CUM_GPA", "desc"), pagination=PaginationSpec(page=1, page_size=2)),
        )

    assert result.total_count == 3
    assert [student.STUD_ID for student in result.rows] == ["1002", "1001"]


def seed_numeric_filter_students(session) -> None:
    session.add_all(
        [
            StudentCurrent(STUD_ID="1001", STUD_NAME="Low", CUM_GPA=2.0, TOTAL_CREDIT_HOURS=30),
            StudentCurrent(STUD_ID="1002", STUD_NAME="Middle", CUM_GPA=3.0, TOTAL_CREDIT_HOURS=60),
            StudentCurrent(STUD_ID="1003", STUD_NAME="High", CUM_GPA=4.0, TOTAL_CREDIT_HOURS=90),
            StudentCurrent(STUD_ID="1004", STUD_NAME="No GPA", CUM_GPA=None, TOTAL_CREDIT_HOURS=None),
        ]
    )
    session.commit()


@pytest.mark.parametrize(
    ("numeric_filter", "expected_ids"),
    [
        (NumericFilter("CUM_GPA", "=", 3.0), ["1002"]),
        (NumericFilter("CUM_GPA", ">", 3.0), ["1003"]),
        (NumericFilter("CUM_GPA", ">=", 3.0), ["1002", "1003"]),
        (NumericFilter("CUM_GPA", "<", 3.0), ["1001"]),
        (NumericFilter("CUM_GPA", "<=", 3.0), ["1001", "1002"]),
        (NumericFilter("CUM_GPA", "between", 2.5, 3.5), ["1002"]),
        (NumericFilter("CUM_GPA", "is empty"), ["1004"]),
        (NumericFilter("CUM_GPA", "is not empty"), ["1001", "1002", "1003"]),
    ],
)
def test_numeric_filter_operators(tmp_path, numeric_filter: NumericFilter, expected_ids: list[str]) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        seed_numeric_filter_students(session)

    with session_factory() as session:
        result = execute_filter_request(session, FilterRequest(numeric_filters=(numeric_filter,)))

    assert [student.STUD_ID for student in result.rows] == expected_ids
    assert result.total_count == len(expected_ids)


def test_numeric_filter_boundary_values(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        seed_numeric_filter_students(session)

    with session_factory() as session:
        result = execute_filter_request(
            session,
            FilterRequest(numeric_filters=(NumericFilter("TOTAL_CREDIT_HOURS", "between", 30, 60),)),
        )

    assert [student.STUD_ID for student in result.rows] == ["1001", "1002"]


def test_numeric_filter_excludes_missing_students_by_default(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add_all(
            [
                StudentCurrent(STUD_ID="1001", CUM_GPA=4.0),
                StudentCurrent(STUD_ID="1002", CUM_GPA=4.0, missing_from_latest_import=True),
            ]
        )
        session.commit()

    with session_factory() as session:
        result = execute_filter_request(session, FilterRequest(numeric_filters=(NumericFilter("CUM_GPA", "=", 4.0),)))

    assert [student.STUD_ID for student in result.rows] == ["1001"]


def seed_boolean_filter_students(session) -> None:
    session.add_all(
        [
            StudentCurrent(
                STUD_ID="1001",
                STUD_NAME="Eligible",
                PROBATION=False,
                FINANCIAL_AID=True,
                DORMS=False,
                REGISTERED_IND=True,
                ENROLLED_IND=True,
                USAID=False,
                MASTER_CARD=False,
                UPP_MEPI=False,
                GAS=False,
                DEANS_WARNING=False,
                DEAN_WARN=False,
            ),
            StudentCurrent(
                STUD_ID="1002",
                STUD_NAME="Probation",
                PROBATION=True,
                FINANCIAL_AID=True,
                DORMS=True,
                REGISTERED_IND=True,
                ENROLLED_IND=False,
                USAID=True,
                MASTER_CARD=False,
                UPP_MEPI=False,
                GAS=False,
                DEANS_WARNING=True,
                DEAN_WARN=True,
            ),
            StudentCurrent(
                STUD_ID="1003",
                STUD_NAME="No Aid",
                PROBATION=False,
                FINANCIAL_AID=False,
                DORMS=False,
                REGISTERED_IND=False,
                ENROLLED_IND=False,
                USAID=False,
                MASTER_CARD=True,
                UPP_MEPI=True,
                GAS=True,
                DEANS_WARNING=False,
                DEAN_WARN=False,
            ),
        ]
    )
    session.commit()


def test_boolean_yes_filter(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        seed_boolean_filter_students(session)

    with session_factory() as session:
        result = execute_filter_request(session, FilterRequest(boolean_filters=(BooleanFilter("PROBATION", True),)))

    assert [student.STUD_ID for student in result.rows] == ["1002"]


def test_boolean_no_filter(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        seed_boolean_filter_students(session)

    with session_factory() as session:
        result = execute_filter_request(session, FilterRequest(boolean_filters=(BooleanFilter("FINANCIAL_AID", False),)))

    assert [student.STUD_ID for student in result.rows] == ["1003"]


def test_boolean_any_filter_is_skipped(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        seed_boolean_filter_students(session)

    with session_factory() as session:
        result = execute_filter_request(session, FilterRequest(boolean_filters=(BooleanFilter("PROBATION", None),)))

    assert [student.STUD_ID for student in result.rows] == ["1001", "1002", "1003"]


def test_boolean_filter_combinations(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        seed_boolean_filter_students(session)

    with session_factory() as session:
        result = execute_filter_request(
            session,
            FilterRequest(
                boolean_filters=(
                    BooleanFilter("PROBATION", False),
                    BooleanFilter("FINANCIAL_AID", True),
                    BooleanFilter("REGISTERED_IND", True),
                    BooleanFilter("ENROLLED_IND", True),
                )
            ),
        )

    assert [student.STUD_ID for student in result.rows] == ["1001"]


@pytest.mark.parametrize(
    "field_name",
    [
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
    ],
)
def test_boolean_filter_accepts_expected_boolean_fields(field_name: str) -> None:
    assert BooleanFilter(field_name, True).field_name == field_name


def seed_category_filter_students(session) -> None:
    session.add_all(
        [
            StudentCurrent(
                STUD_ID="1001",
                STUD_NAME="CS Senior",
                MAJR_DESC="Computer Science",
                CLAS_DESC="Senior",
                COLL_CODE="AS",
                STST_DESC="Active",
                LEVL_CODE="UG",
            ),
            StudentCurrent(
                STUD_ID="1002",
                STUD_NAME="Business Junior",
                MAJR_DESC="Business & Management",
                CLAS_DESC="Junior",
                COLL_CODE="BUS",
                STST_DESC="Active",
                LEVL_CODE="UG",
            ),
            StudentCurrent(
                STUD_ID="1003",
                STUD_NAME="No Major",
                MAJR_DESC=None,
                CLAS_DESC="Sophomore",
                COLL_CODE=None,
                STST_DESC="Inactive",
                LEVL_CODE="UG",
            ),
        ]
    )
    session.commit()


def test_category_single_select_filter(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        seed_category_filter_students(session)

    with session_factory() as session:
        result = execute_filter_request(session, FilterRequest(category_filters=(CategoryFilter("MAJR_DESC", ("Computer Science",)),)))

    assert [student.STUD_ID for student in result.rows] == ["1001"]


def test_category_multi_select_filter(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        seed_category_filter_students(session)

    with session_factory() as session:
        result = execute_filter_request(
            session,
            FilterRequest(category_filters=(CategoryFilter("CLAS_DESC", ("Senior", "Junior")),)),
        )

    assert [student.STUD_ID for student in result.rows] == ["1001", "1002"]


def test_category_filter_handles_special_characters(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        seed_category_filter_students(session)

    with session_factory() as session:
        result = execute_filter_request(
            session,
            FilterRequest(category_filters=(CategoryFilter("MAJR_DESC", ("Business & Management",)),)),
        )

    assert [student.STUD_ID for student in result.rows] == ["1002"]


def test_category_empty_value_filter(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        seed_category_filter_students(session)

    with session_factory() as session:
        result = execute_filter_request(session, FilterRequest(category_filters=(CategoryFilter("MAJR_DESC", (None,)),)))

    assert [student.STUD_ID for student in result.rows] == ["1003"]


def test_category_filter_applies_to_expected_category_fields(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        seed_category_filter_students(session)

    cases = [
        (CategoryFilter("COLL_CODE", ("AS",)), ["1001"]),
        (CategoryFilter("STST_DESC", ("Inactive",)), ["1003"]),
        (CategoryFilter("LEVL_CODE", ("UG",)), ["1001", "1002", "1003"]),
    ]

    for category_filter, expected_ids in cases:
        with session_factory() as session:
            result = execute_filter_request(session, FilterRequest(category_filters=(category_filter,)))
        assert [student.STUD_ID for student in result.rows] == expected_ids


def seed_text_filter_students(session) -> None:
    session.add_all(
        [
            StudentCurrent(
                STUD_ID="1001",
                STUD_NAME="Alice Example",
                STUD_EMAIL="alice@example.com",
                WSP_TECHNICAL_SKILLS="Python, Excel, data analysis",
                WSP_SPOKEN_LANGUAGES="English, Arabic",
                WSP_PREV_WORK="Office assistant",
                WSP_PREFERRED_TYPE_OF_WORK="Administrative work",
            ),
            StudentCurrent(
                STUD_ID="1002",
                STUD_NAME="Bob Percent",
                STUD_EMAIL="bob@example.com",
                WSP_TECHNICAL_SKILLS="SQL 100% literal, reporting",
                WSP_SPOKEN_LANGUAGES="French",
                WSP_PREV_WORK="Data entry",
                WSP_PREFERRED_TYPE_OF_WORK="Research",
            ),
            StudentCurrent(
                STUD_ID="1003",
                STUD_NAME="Carol Blank",
                STUD_EMAIL="carol@example.com",
                WSP_TECHNICAL_SKILLS=None,
                WSP_SPOKEN_LANGUAGES="",
                WSP_PREV_WORK="Teaching assistant",
                WSP_PREFERRED_TYPE_OF_WORK="Tutoring",
            ),
            StudentCurrent(
                STUD_ID="1004",
                STUD_NAME="Robert'); DROP TABLE students_current; --",
                STUD_EMAIL="robert@example.com",
                WSP_TECHNICAL_SKILLS="Security testing",
                WSP_SPOKEN_LANGUAGES="English",
                WSP_PREV_WORK="IT support",
                WSP_PREFERRED_TYPE_OF_WORK="Technical work",
            ),
        ]
    )
    session.commit()


def test_text_contains_is_case_insensitive(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        seed_text_filter_students(session)

    with session_factory() as session:
        result = execute_filter_request(
            session,
            FilterRequest(text_filters=(TextFilter("WSP_TECHNICAL_SKILLS", "contains", "python"),)),
        )

    assert [student.STUD_ID for student in result.rows] == ["1001"]


def test_text_exact_match(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        seed_text_filter_students(session)

    with session_factory() as session:
        result = execute_filter_request(session, FilterRequest(text_filters=(TextFilter("STUD_NAME", "exact match", "alice example"),)))

    assert [student.STUD_ID for student in result.rows] == ["1001"]


def test_text_starts_with_and_ends_with(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        seed_text_filter_students(session)

    with session_factory() as session:
        starts = execute_filter_request(session, FilterRequest(text_filters=(TextFilter("STUD_EMAIL", "starts with", "bob"),)))
        ends = execute_filter_request(session, FilterRequest(text_filters=(TextFilter("STUD_EMAIL", "ends with", "example.com"),)))

    assert [student.STUD_ID for student in starts.rows] == ["1002"]
    assert [student.STUD_ID for student in ends.rows] == ["1001", "1002", "1003", "1004"]


def test_text_empty_values(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        seed_text_filter_students(session)

    with session_factory() as session:
        empty_result = execute_filter_request(session, FilterRequest(text_filters=(TextFilter("WSP_TECHNICAL_SKILLS", "is empty"),)))
        not_empty_result = execute_filter_request(session, FilterRequest(text_filters=(TextFilter("WSP_TECHNICAL_SKILLS", "is not empty"),)))

    assert [student.STUD_ID for student in empty_result.rows] == ["1003"]
    assert [student.STUD_ID for student in not_empty_result.rows] == ["1001", "1002", "1004"]


def test_text_does_not_contain_includes_nulls(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        seed_text_filter_students(session)

    with session_factory() as session:
        result = execute_filter_request(session, FilterRequest(text_filters=(TextFilter("WSP_TECHNICAL_SKILLS", "does not contain", "Python"),)))

    assert [student.STUD_ID for student in result.rows] == ["1002", "1003", "1004"]


def test_text_special_characters_are_treated_as_literal_text(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        seed_text_filter_students(session)

    with session_factory() as session:
        percent_result = execute_filter_request(session, FilterRequest(text_filters=(TextFilter("WSP_TECHNICAL_SKILLS", "contains", "100%"),)))
        wildcard_result = execute_filter_request(session, FilterRequest(text_filters=(TextFilter("WSP_TECHNICAL_SKILLS", "contains", "%"),)))

    assert [student.STUD_ID for student in percent_result.rows] == ["1002"]
    assert [student.STUD_ID for student in wildcard_result.rows] == ["1002"]


def test_sql_injection_like_text_is_treated_as_text(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    injection_like_text = "Robert'); DROP TABLE students_current; --"

    with session_factory() as session:
        seed_text_filter_students(session)

    with session_factory() as session:
        result = execute_filter_request(session, FilterRequest(text_filters=(TextFilter("STUD_NAME", "exact match", injection_like_text),)))
        still_exists_count = session.query(StudentCurrent).count()

    assert [student.STUD_ID for student in result.rows] == ["1004"]
    assert still_exists_count == 4


def seed_combined_filter_students(session) -> None:
    session.add_all(
        [
            StudentCurrent(
                STUD_ID="1001",
                STUD_NAME="Alice Analyst",
                CUM_GPA=3.8,
                PROBATION=False,
                FINANCIAL_AID=True,
                MAJR_DESC="Computer Science",
                CLAS_DESC="Senior",
                COLL_CODE="AS",
                WSP_TECHNICAL_SKILLS="Python, Excel, SQL",
            ),
            StudentCurrent(
                STUD_ID="1002",
                STUD_NAME="Bob Builder",
                CUM_GPA=2.9,
                PROBATION=False,
                FINANCIAL_AID=True,
                MAJR_DESC="Computer Science",
                CLAS_DESC="Junior",
                COLL_CODE="AS",
                WSP_TECHNICAL_SKILLS="Excel",
            ),
            StudentCurrent(
                STUD_ID="1003",
                STUD_NAME="Carol Coordinator",
                CUM_GPA=3.9,
                PROBATION=True,
                FINANCIAL_AID=False,
                MAJR_DESC="Business",
                CLAS_DESC="Senior",
                COLL_CODE="BUS",
                WSP_TECHNICAL_SKILLS="Python, reporting",
            ),
            StudentCurrent(
                STUD_ID="1004",
                STUD_NAME="Dana Data",
                CUM_GPA=3.5,
                PROBATION=False,
                FINANCIAL_AID=True,
                MAJR_DESC="Computer Science",
                CLAS_DESC="Senior",
                COLL_CODE="AS",
                WSP_TECHNICAL_SKILLS="Python, data entry",
            ),
        ]
    )
    session.commit()


def test_combined_numeric_plus_boolean_filters(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        seed_combined_filter_students(session)

    with session_factory() as session:
        result = execute_filter_request(
            session,
            FilterRequest(
                numeric_filters=(NumericFilter("CUM_GPA", ">=", 3.5),),
                boolean_filters=(BooleanFilter("PROBATION", False),),
            ),
        )

    assert [student.STUD_ID for student in result.rows] == ["1001", "1004"]


def test_combined_category_plus_text_filters(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        seed_combined_filter_students(session)

    with session_factory() as session:
        result = execute_filter_request(
            session,
            FilterRequest(
                category_filters=(CategoryFilter("MAJR_DESC", ("Computer Science",)),),
                text_filters=(TextFilter("WSP_TECHNICAL_SKILLS", "contains", "Python"),),
            ),
        )

    assert [student.STUD_ID for student in result.rows] == ["1001", "1004"]


def test_combined_all_supported_filter_types_together(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        seed_combined_filter_students(session)

    with session_factory() as session:
        result = execute_filter_request(
            session,
            FilterRequest(
                numeric_filters=(NumericFilter("CUM_GPA", ">=", 3.6),),
                boolean_filters=(BooleanFilter("PROBATION", False), BooleanFilter("FINANCIAL_AID", True)),
                category_filters=(CategoryFilter("CLAS_DESC", ("Senior",)),),
                text_filters=(TextFilter("WSP_TECHNICAL_SKILLS", "contains", "SQL"),),
            ),
        )

    assert [student.STUD_ID for student in result.rows] == ["1001"]
    assert result.applied_filter_count == 5


def test_combined_filters_support_pagination(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        seed_combined_filter_students(session)

    with session_factory() as session:
        result = execute_filter_request(
            session,
            FilterRequest(
                boolean_filters=(BooleanFilter("PROBATION", False),),
                pagination=PaginationSpec(page=2, page_size=1),
            ),
        )

    assert result.total_count == 3
    assert result.page == 2
    assert [student.STUD_ID for student in result.rows] == ["1002"]


def test_combined_filters_support_sorting(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        seed_combined_filter_students(session)

    with session_factory() as session:
        result = execute_filter_request(
            session,
            FilterRequest(
                boolean_filters=(BooleanFilter("PROBATION", False),),
                sort=SortSpec("CUM_GPA", "desc"),
            ),
        )

    assert [student.STUD_ID for student in result.rows] == ["1001", "1004", "1002"]


def test_combined_filters_return_selected_columns_and_metadata(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        seed_combined_filter_students(session)

    request = FilterRequest(
        numeric_filters=(NumericFilter("CUM_GPA", ">=", 3.6),),
        selected_columns=("STUD_ID", "STUD_NAME", "CUM_GPA"),
        sort=SortSpec("STUD_ID"),
    )
    with session_factory() as session:
        result = execute_filter_request(session, request)

    assert result.selected_rows == (
        {"STUD_ID": "1001", "STUD_NAME": "Alice Analyst", "CUM_GPA": 3.8},
        {"STUD_ID": "1003", "STUD_NAME": "Carol Coordinator", "CUM_GPA": 3.9},
    )
    assert result.applied_filter_metadata["numeric_filters"] == [
        {"field_name": "CUM_GPA", "operator": ">=", "value": 3.6, "value_to": None}
    ]
    assert result.applied_filter_metadata["selected_columns"] == ("STUD_ID", "STUD_NAME", "CUM_GPA")


def test_filter_results_can_select_student_audit_timestamps(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add(StudentCurrent(STUD_ID="1001", STUD_NAME="Audit Student"))
        session.commit()

    with session_factory() as session:
        result = execute_filter_request(
            session,
            FilterRequest(selected_columns=("STUD_ID", "added_to_db_at", "modified_in_db_at")),
        )

    assert result.selected_rows[0]["STUD_ID"] == "1001"
    assert result.selected_rows[0]["added_to_db_at"] is not None
    assert result.selected_rows[0]["modified_in_db_at"] is None


def test_filter_request_json_round_trip() -> None:
    request = FilterRequest(
        numeric_filters=(NumericFilter("CUM_GPA", ">=", 3.0),),
        boolean_filters=(BooleanFilter("PROBATION", False),),
        category_filters=(CategoryFilter("MAJR_DESC", ("Computer Science",)),),
        text_filters=(TextFilter("WSP_TECHNICAL_SKILLS", "contains", "Python"),),
        sort=SortSpec("CUM_GPA", "desc"),
        pagination=PaginationSpec(page=2, page_size=10),
        selected_columns=("STUD_ID", "CUM_GPA"),
    )

    restored = filter_request_from_json(filter_request_to_json(request))

    assert restored == request


def test_save_and_load_filter_preset_round_trip(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    request = FilterRequest(numeric_filters=(NumericFilter("CUM_GPA", ">=", 3.0),))

    with session_factory() as session:
        preset = save_filter_preset(session, "High GPA", request)
        session.commit()
        preset_id = preset.preset_id

    with session_factory() as session:
        loaded = load_filter_preset(session, "High GPA")
        stored = session.get(FilterPreset, preset_id)

    assert loaded == request
    assert stored is not None
    assert stored.preset_name == "High GPA"


def test_duplicate_filter_preset_name_is_rejected(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        save_filter_preset(session, "High GPA", FilterRequest())
        session.commit()

        with pytest.raises(FilterPresetError, match="already exists"):
            save_filter_preset(session, "High GPA", FilterRequest())


def test_invalid_preset_cannot_run(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add(
            FilterPreset(
                preset_name="Broken",
                filter_json={"numeric_filters": [{"field_name": "NOT_A_FIELD", "operator": ">=", "value": 3.0}]},
            )
        )
        session.commit()

    with session_factory() as session:
        with pytest.raises(FilterValidationError, match="Invalid filter field"):
            load_filter_preset(session, "Broken")


def test_rename_filter_preset(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        preset = save_filter_preset(session, "Old Name", FilterRequest())
        session.commit()
        preset_id = preset.preset_id

        rename_filter_preset(session, preset_id, "New Name")
        session.commit()

    with session_factory() as session:
        assert load_filter_preset(session, "New Name") == FilterRequest()


def test_delete_filter_preset_does_not_affect_students(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        preset = save_filter_preset(session, "Temporary", FilterRequest())
        session.add(StudentCurrent(STUD_ID="1001", STUD_NAME="Still Here"))
        session.commit()
        preset_id = preset.preset_id

        delete_filter_preset(session, preset_id)
        session.commit()

    with session_factory() as session:
        assert session.query(FilterPreset).count() == 0
        assert session.query(StudentCurrent).count() == 1


def test_load_or_delete_missing_preset_raises_clear_error(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        with pytest.raises(FilterPresetError, match="was not found"):
            load_filter_preset(session, "Missing")

        with pytest.raises(FilterPresetError, match="was not found"):
            delete_filter_preset(session, 999)


def test_filter_run_log_is_created(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    request = FilterRequest(numeric_filters=(NumericFilter("CUM_GPA", ">=", 3.0),))

    with session_factory() as session:
        filter_run = log_filter_run(session, request=request, result_count=12)
        session.commit()
        filter_run_id = filter_run.filter_run_id

    with session_factory() as session:
        stored = session.get(FilterRun, filter_run_id)

    assert stored is not None
    assert stored.result_count == 12
    assert stored.filter_json["numeric_filters"][0]["field_name"] == "CUM_GPA"


def test_filter_run_log_stores_result_count_and_preset_id(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        preset = save_filter_preset(session, "High GPA", FilterRequest())
        session.commit()

        filter_run = log_filter_run(session, request=FilterRequest(), result_count=4, preset_id=preset.preset_id)
        session.commit()
        filter_run_id = filter_run.filter_run_id

    with session_factory() as session:
        stored = session.get(FilterRun, filter_run_id)

    assert stored is not None
    assert stored.result_count == 4
    assert stored.preset_id == preset.preset_id


def test_export_link_is_added_when_export_happens(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        filter_run = log_filter_run(session, request=FilterRequest(), result_count=2)
        session.commit()

        export_log = log_filter_export(
            session,
            filter_run_id=filter_run.filter_run_id,
            export_path="C:/exports/results.xlsx",
            row_count=2,
        )
        session.commit()
        export_id = export_log.export_id

    with session_factory() as session:
        stored = session.get(ExportLog, export_id)

    assert stored is not None
    assert stored.filter_run_id == filter_run.filter_run_id
    assert stored.export_path == "C:/exports/results.xlsx"
    assert stored.row_count == 2


def test_export_log_requires_existing_filter_run(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        with pytest.raises(FilterPresetError, match="Filter run was not found"):
            log_filter_export(session, filter_run_id=999, export_path="C:/exports/results.xlsx", row_count=0)


def test_semantic_filter_combines_with_numeric_filter(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add_all(
            [
                StudentCurrent(STUD_ID="1001", CUM_GPA=3.8, WSP_TECHNICAL_SKILLS="Python"),
                StudentCurrent(STUD_ID="1002", CUM_GPA=2.9, WSP_TECHNICAL_SKILLS="Excel"),
                StudentCurrent(STUD_ID="1003", CUM_GPA=3.9, WSP_TECHNICAL_SKILLS="SQL"),
            ]
        )
        session.commit()

    def fake_ranker(semantic_filter: SemanticFilter, candidate_rows: tuple[StudentCurrent, ...]) -> tuple[SemanticMatch, ...]:
        assert semantic_filter.query == "data work"
        assert [student.STUD_ID for student in candidate_rows] == ["1001", "1003"]
        return (
            SemanticMatch("1003", 0.92, "database fit"),
            SemanticMatch("1001", 0.73, "coding fit"),
        )

    with session_factory() as session:
        result = execute_filter_request(
            session,
            FilterRequest(
                numeric_filters=(NumericFilter("CUM_GPA", ">=", 3.5),),
                semantic_filter=SemanticFilter("data work"),
                selected_columns=("STUD_ID", "CUM_GPA"),
            ),
            semantic_ranker=fake_ranker,
        )

    assert [student.STUD_ID for student in result.rows] == ["1003", "1001"]
    assert result.total_count == 2
    assert result.semantic_scores == {"1003": 0.92, "1001": 0.73}
    assert result.selected_rows == (
        {"STUD_ID": "1003", "CUM_GPA": 3.9, "semantic_score": 0.92, "semantic_explanation": "database fit"},
        {"STUD_ID": "1001", "CUM_GPA": 3.8, "semantic_score": 0.73, "semantic_explanation": "coding fit"},
    )
    assert result.applied_filter_metadata["semantic_result_count"] == 2


def test_semantic_filter_combines_with_boolean_filter(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add_all(
            [
                StudentCurrent(STUD_ID="1001", FINANCIAL_AID=True, WSP_PREFERRED_TYPE_OF_WORK="Research"),
                StudentCurrent(STUD_ID="1002", FINANCIAL_AID=True, WSP_PREFERRED_TYPE_OF_WORK="Data entry"),
                StudentCurrent(STUD_ID="1003", FINANCIAL_AID=False, WSP_PREFERRED_TYPE_OF_WORK="Data entry"),
            ]
        )
        session.commit()

    def fake_ranker(semantic_filter: SemanticFilter, candidate_rows: tuple[StudentCurrent, ...]) -> tuple[SemanticMatch, ...]:
        assert semantic_filter.top_k == 1
        assert [student.STUD_ID for student in candidate_rows] == ["1001", "1002"]
        return (SemanticMatch("1002", 0.95, "best match"),)

    with session_factory() as session:
        result = execute_filter_request(
            session,
            FilterRequest(
                boolean_filters=(BooleanFilter("FINANCIAL_AID", True),),
                semantic_filter=SemanticFilter("data entry", top_k=1),
            ),
            semantic_ranker=fake_ranker,
        )

    assert [student.STUD_ID for student in result.rows] == ["1002"]
    assert result.total_count == 1
    assert result.applied_filter_count == 2
