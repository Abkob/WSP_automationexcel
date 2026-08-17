from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any

from sqlalchemy import case, or_

from database.models import ImportBatch, StudentCurrent, StudentHistory


PROFILE_GROUPS: tuple[tuple[str, str, tuple[tuple[str, str], ...]], ...] = (
    (
        "academic",
        "Academic & enrollment",
        (
            ("Major", "MAJR_DESC"),
            ("Class / year", "CLAS_DESC"),
            ("Cumulative GPA", "CUM_GPA"),
            ("Total credit hours", "TOTAL_CREDIT_HOURS"),
            ("Enrollment term", "ENRL_TERM"),
            ("Student status", "STST_DESC"),
            ("Student type", "STYP_DESC"),
            ("Student type code", "STYP_CODE"),
            ("Level code", "LEVL_CODE"),
            ("College code", "COLL_CODE"),
            ("Enrolled", "ENROLLED_IND"),
            ("Registered", "REGISTERED_IND"),
        ),
    ),
    (
        "standing",
        "Academic standing",
        (
            ("Standing", "ASTD_DESC"),
            ("Standing code", "ATSD_CODE_END_OF_TERM"),
            ("Standing term", "ASTD_TERM"),
            ("Standing date", "ASTD_DATE_END_OF_TERM"),
            ("Probation", "PROBATION"),
            ("Dean's warning", "DEANS_WARNING"),
            ("Dean warning flag", "DEAN_WARN"),
        ),
    ),
    (
        "contact",
        "Contact information",
        (
            ("AUB email", "STUD_EMAIL"),
            ("Mobile number", "MOBILE_NBR"),
            ("Application date", "APPLICATION_DATE"),
        ),
    ),
    (
        "work",
        "Work-study experience & preferences",
        (
            ("Previous work experience", "WSP_PREV_WORK"),
            ("Previous type of work", "WSP_PREVIOUS_TYPE_OF_WORK"),
            ("Preferred type of work", "WSP_PREFERRED_TYPE_OF_WORK"),
        ),
    ),
)

SKILL_FIELDS: tuple[tuple[str, str], ...] = (
    ("Technical skills", "WSP_TECHNICAL_SKILLS"),
    ("Organizational skills", "WSP_ORGANIZATIONAL_SKILLS"),
    ("Interpersonal skills", "WSP_INTERPERSONAL_SKILLS"),
    ("Additional skills", "WSP_ADDITIONAL_SKILLS"),
    ("Spoken languages", "WSP_SPOKEN_LANGUAGES"),
    ("Written languages", "WSP_WRITTEN_LANGUAGES"),
)

SUPPORT_FIELDS: tuple[tuple[str, str], ...] = (
    ("Financial aid", "FINANCIAL_AID"),
    ("USAID", "USAID"),
    ("Mastercard Foundation", "MASTER_CARD"),
    ("UPP / MEPI", "UPP_MEPI"),
    ("GAS", "GAS"),
    ("Dorms", "DORMS"),
)


def lookup_students(session, query: str, *, limit: int = 12) -> list[dict[str, Any]]:
    clean_query = str(query or "").strip()
    limit = max(1, min(int(limit), 25))
    statement = session.query(StudentCurrent)
    if clean_query:
        pattern = f"%{clean_query}%"
        statement = statement.filter(
            or_(
                StudentCurrent.STUD_ID.ilike(pattern),
                StudentCurrent.STUD_NAME.ilike(pattern),
                StudentCurrent.STUD_EMAIL.ilike(pattern),
                StudentCurrent.MAJR_DESC.ilike(pattern),
            )
        )
    students = (
        statement.order_by(
            case((StudentCurrent.STUD_ID == clean_query, 0), else_=1),
            StudentCurrent.missing_from_latest_import.asc(),
            StudentCurrent.STUD_NAME.asc(),
            StudentCurrent.STUD_ID.asc(),
        )
        .limit(limit)
        .all()
    )
    return [
        {
            "student_id": student.STUD_ID,
            "name": student.STUD_NAME or "Unnamed student",
            "major": student.MAJR_DESC or "Major not provided",
            "class_year": student.CLAS_DESC or "Class not provided",
            "email": student.STUD_EMAIL or "",
            "gpa": student.CUM_GPA,
            "is_current": not student.missing_from_latest_import,
        }
        for student in students
    ]


def build_student_profile_payload(session, student_id: str) -> dict[str, Any] | None:
    student = (
        session.query(StudentCurrent)
        .filter(StudentCurrent.STUD_ID == str(student_id).strip())
        .first()
    )
    if student is None:
        return None

    batch_ids = {student.first_seen_batch_id, student.last_seen_batch_id}
    histories = (
        session.query(StudentHistory)
        .filter(StudentHistory.STUD_ID == student.STUD_ID)
        .order_by(StudentHistory.created_at.desc(), StudentHistory.history_id.desc())
        .limit(25)
        .all()
    )
    batch_ids.update(history.batch_id for history in histories)
    batches = {
        batch.batch_id: batch
        for batch in session.query(ImportBatch).filter(ImportBatch.batch_id.in_([item for item in batch_ids if item])).all()
    }

    profile_groups = []
    for key, title, fields in PROFILE_GROUPS:
        profile_groups.append(
            {
                "key": key,
                "title": title,
                "items": [
                    {
                        "label": label,
                        "field": field,
                        "value": _json_value(getattr(student, field)),
                        "kind": _value_kind(getattr(student, field)),
                    }
                    for label, field in fields
                ],
            }
        )

    skills = [
        {
            "label": label,
            "field": field,
            "raw": getattr(student, field),
            "values": _split_tags(getattr(student, field)),
        }
        for label, field in SKILL_FIELDS
    ]
    support = [
        {"label": label, "field": field, "value": getattr(student, field)}
        for label, field in SUPPORT_FIELDS
    ]
    extras = [
        {"label": _humanize_key(key), "field": key, "value": _json_value(value), "kind": _value_kind(value)}
        for key, value in sorted((student.extra_columns_json or {}).items())
    ]

    timeline = []
    for history in histories:
        batch = batches.get(history.batch_id)
        timeline.append(
            {
                "type": history.change_type,
                "title": _history_title(history.change_type),
                "date": _json_value(history.created_at or history.valid_to or history.valid_from),
                "batch_id": history.batch_id,
                "source": batch.filename if batch else None,
            }
        )
    if student.added_to_db_at:
        first_batch = batches.get(student.first_seen_batch_id)
        timeline.append(
            {
                "type": "added",
                "title": "Student record added",
                "date": _json_value(student.added_to_db_at),
                "batch_id": student.first_seen_batch_id,
                "source": first_batch.filename if first_batch else None,
            }
        )
    timeline.sort(key=lambda item: item.get("date") or "", reverse=True)

    standing = student.ASTD_DESC or student.STST_DESC or ("Probation" if student.PROBATION else "No standing alert")
    badges = _build_badges(student)
    return {
        "identity": {
            "student_id": student.STUD_ID,
            "name": student.STUD_NAME or "Unnamed student",
            "email": student.STUD_EMAIL,
            "mobile": student.MOBILE_NBR,
            "major": student.MAJR_DESC,
            "class_year": student.CLAS_DESC,
            "is_current": not student.missing_from_latest_import,
            "initials": _initials(student.STUD_NAME),
        },
        "overview": _build_overview(student),
        "badges": badges,
        "highlights": [
            {"label": "Cumulative GPA", "value": _format_metric(student.CUM_GPA, decimals=2), "detail": "Current record"},
            {"label": "Credit hours", "value": _format_metric(student.TOTAL_CREDIT_HOURS, decimals=1), "detail": "Total earned / recorded"},
            {"label": "Academic standing", "value": standing, "detail": student.ASTD_TERM or "Latest available"},
            {"label": "Enrollment", "value": _enrollment_label(student), "detail": student.ENRL_TERM or "Term not provided"},
        ],
        "groups": profile_groups,
        "skills": skills,
        "support": support,
        "additional_fields": extras,
        "record": {
            "is_current": not student.missing_from_latest_import,
            "added_at": _json_value(student.added_to_db_at),
            "modified_at": _json_value(student.modified_in_db_at),
            "created_at": _json_value(student.created_at),
            "updated_at": _json_value(student.updated_at),
            "first_seen_batch_id": student.first_seen_batch_id,
            "first_seen_source": batches.get(student.first_seen_batch_id).filename if batches.get(student.first_seen_batch_id) else None,
            "last_seen_batch_id": student.last_seen_batch_id,
            "last_seen_source": batches.get(student.last_seen_batch_id).filename if batches.get(student.last_seen_batch_id) else None,
        },
        "timeline": timeline,
    }


def _split_tags(value: str | None) -> list[str]:
    if not value:
        return []
    parts = re.split(r"[,;\n|]+", str(value))
    return [part.strip() for part in parts if part.strip()]


def _initials(name: str | None) -> str:
    words = [word for word in re.split(r"\s+", name or "") if word]
    return "".join(word[0].upper() for word in words[:2]) or "ST"


def _build_badges(student: StudentCurrent) -> list[dict[str, str]]:
    badges = [{"label": "Current record" if not student.missing_from_latest_import else "Missing from latest import", "tone": "good" if not student.missing_from_latest_import else "muted"}]
    if student.ENROLLED_IND is True:
        badges.append({"label": "Enrolled", "tone": "blue"})
    if student.REGISTERED_IND is True:
        badges.append({"label": "Registered", "tone": "blue"})
    if student.PROBATION is True:
        badges.append({"label": "Probation", "tone": "danger"})
    if student.DEANS_WARNING is True or student.DEAN_WARN is True:
        badges.append({"label": "Dean's warning", "tone": "warn"})
    if student.FINANCIAL_AID is True:
        badges.append({"label": "Financial aid", "tone": "aub"})
    return badges


def _build_overview(student: StudentCurrent) -> str:
    name = student.STUD_NAME or f"Student {student.STUD_ID}"
    academic = " ".join(part for part in (student.CLAS_DESC, student.MAJR_DESC) if part)
    text = f"{name} is"
    text += f" a {academic} student" if academic else " a student"
    if student.CUM_GPA is not None:
        text += f" with a {student.CUM_GPA:.2f} cumulative GPA"
    if student.TOTAL_CREDIT_HOURS is not None:
        text += f" and {student.TOTAL_CREDIT_HOURS:g} recorded credit hours"
    text += "."
    preference = (student.WSP_PREFERRED_TYPE_OF_WORK or "").strip()
    if preference:
        text += f" Their stated work preference is {preference.rstrip('.')} .".replace(" .", ".")
    return text


def _enrollment_label(student: StudentCurrent) -> str:
    if student.ENROLLED_IND is True and student.REGISTERED_IND is True:
        return "Enrolled & registered"
    if student.ENROLLED_IND is True:
        return "Enrolled"
    if student.REGISTERED_IND is True:
        return "Registered"
    if student.ENROLLED_IND is False and student.REGISTERED_IND is False:
        return "Not enrolled"
    return "Not provided"


def _format_metric(value: float | int | None, *, decimals: int) -> str:
    if value is None:
        return "Not provided"
    number = float(value)
    if decimals == 1 and number.is_integer():
        return str(int(number))
    return f"{number:.{decimals}f}"


def _history_title(change_type: str) -> str:
    return {
        "updated_student": "Student record updated",
        "missing_from_latest_import": "Missing from an import",
        "added_student": "Student record added",
    }.get(change_type, _humanize_key(change_type))


def _humanize_key(value: str) -> str:
    return str(value).replace("_", " ").strip().title()


def _value_kind(value: Any) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, (date, datetime)):
        return "date"
    return "text"


def _json_value(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value
