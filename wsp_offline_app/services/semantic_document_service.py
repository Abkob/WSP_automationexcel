from __future__ import annotations

import json
import re
from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Iterable

from database.models import StudentCurrent


SEMANTIC_PROFILE_SOURCE_COLUMN = "student_profile"
SEMANTIC_PROFILE_FIELDS = (
    "MAJR_DESC",
    "CLAS_DESC",
    "CUM_GPA",
    "PROBATION",
    "FINANCIAL_AID",
    "DORMS",
    "ENROLLED_IND",
    "REGISTERED_IND",
    "WSP_TECHNICAL_SKILLS",
    "WSP_ORGANIZATIONAL_SKILLS",
    "WSP_INTERPERSONAL_SKILLS",
    "WSP_ADDITIONAL_SKILLS",
    "WSP_PREVIOUS_TYPE_OF_WORK",
    "WSP_PREFERRED_TYPE_OF_WORK",
    "WSP_PREV_WORK",
    "WSP_WRITTEN_LANGUAGES",
    "WSP_SPOKEN_LANGUAGES",
)
PRIVATE_SEMANTIC_PROFILE_FIELDS = (
    "STUD_ID",
    "STUD_NAME",
    "STUD_EMAIL",
    "MOBILE_NBR",
)
PRIVATE_FIELD_TOKENS = ("EMAIL", "MOBILE", "PHONE", "NAME", "STUD_ID")
FIELD_LABELS = {
    "MAJR_DESC": "Major",
    "CLAS_DESC": "Class",
    "CUM_GPA": "GPA",
    "PROBATION": "Probation",
    "FINANCIAL_AID": "Financial aid",
    "DORMS": "Dorms",
    "ENROLLED_IND": "Enrolled",
    "REGISTERED_IND": "Registered",
    "WSP_TECHNICAL_SKILLS": "Technical skills",
    "WSP_ORGANIZATIONAL_SKILLS": "Organizational skills",
    "WSP_INTERPERSONAL_SKILLS": "Interpersonal skills",
    "WSP_ADDITIONAL_SKILLS": "Additional skills",
    "WSP_PREVIOUS_TYPE_OF_WORK": "Previous type of work",
    "WSP_PREFERRED_TYPE_OF_WORK": "Preferred type of work",
    "WSP_PREV_WORK": "Previous work",
    "WSP_WRITTEN_LANGUAGES": "Written languages",
    "WSP_SPOKEN_LANGUAGES": "Spoken languages",
}
WHITESPACE_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class StudentSemanticProfile:
    STUD_ID: str
    text: str
    fields: dict[str, str]
    metadata: dict[str, Any]
    document_hash: str


def build_student_semantic_profile(
    student: StudentCurrent,
    *,
    include_private_fields: bool = False,
    source_fields: Iterable[str] = SEMANTIC_PROFILE_FIELDS,
) -> StudentSemanticProfile:
    fields = collect_semantic_profile_fields(
        student,
        include_private_fields=include_private_fields,
        source_fields=source_fields,
    )
    metadata = build_semantic_profile_metadata(student)
    text = format_student_semantic_profile(fields)
    profile_without_hash = {
        "STUD_ID": clean_profile_value(getattr(student, "STUD_ID", "")),
        "fields": fields,
        "metadata": metadata,
        "text": text,
    }
    document_hash = hash_semantic_profile_payload(profile_without_hash)
    return StudentSemanticProfile(
        STUD_ID=profile_without_hash["STUD_ID"],
        text=text,
        fields=fields,
        metadata=metadata,
        document_hash=document_hash,
    )


def build_student_semantic_profiles(students: Iterable[StudentCurrent]) -> tuple[StudentSemanticProfile, ...]:
    profiles = []
    for student in students:
        profile = build_student_semantic_profile(student)
        if profile.text:
            profiles.append(profile)
    return tuple(profiles)


def collect_semantic_profile_fields(
    student: StudentCurrent,
    *,
    include_private_fields: bool,
    source_fields: Iterable[str],
) -> dict[str, str]:
    fields: dict[str, str] = {}
    for field_name in source_fields:
        if not include_private_fields and is_private_semantic_profile_field(field_name):
            continue
        value = clean_profile_value(getattr(student, field_name, None))
        if value:
            fields[field_name] = value
    return fields


def build_semantic_profile_metadata(student: StudentCurrent) -> dict[str, Any]:
    return {
        "STUD_ID": clean_profile_value(getattr(student, "STUD_ID", "")),
        "major": clean_profile_value(getattr(student, "MAJR_DESC", "")),
        "class": clean_profile_value(getattr(student, "CLAS_DESC", "")),
        "gpa": getattr(student, "CUM_GPA", None),
        "probation": getattr(student, "PROBATION", None),
        "financial_aid": getattr(student, "FINANCIAL_AID", None),
        "dorms": getattr(student, "DORMS", None),
        "missing_from_latest_import": getattr(student, "missing_from_latest_import", False),
    }


def format_student_semantic_profile(fields: dict[str, str]) -> str:
    sections: list[str] = ["Student profile for work-study matching."]
    append_profile_section(sections, "Academic", fields, ("MAJR_DESC", "CLAS_DESC", "CUM_GPA"))
    append_profile_section(sections, "Eligibility", fields, ("PROBATION", "FINANCIAL_AID", "DORMS", "ENROLLED_IND", "REGISTERED_IND"))
    append_profile_section(
        sections,
        "Work preferences and experience",
        fields,
        ("WSP_PREFERRED_TYPE_OF_WORK", "WSP_PREVIOUS_TYPE_OF_WORK", "WSP_PREV_WORK"),
    )
    append_profile_section(
        sections,
        "Skills",
        fields,
        (
            "WSP_TECHNICAL_SKILLS",
            "WSP_ORGANIZATIONAL_SKILLS",
            "WSP_INTERPERSONAL_SKILLS",
            "WSP_ADDITIONAL_SKILLS",
        ),
    )
    append_profile_section(sections, "Languages", fields, ("WSP_WRITTEN_LANGUAGES", "WSP_SPOKEN_LANGUAGES"))
    return "\n\n".join(section for section in sections if section.strip())


def append_profile_section(sections: list[str], title: str, fields: dict[str, str], field_names: tuple[str, ...]) -> None:
    lines = [f"{semantic_profile_field_label(field_name)}: {fields[field_name]}" for field_name in field_names if fields.get(field_name)]
    if lines:
        sections.append(f"{title}:\n" + "\n".join(lines))


def hash_semantic_profile(profile: StudentSemanticProfile) -> str:
    return hash_semantic_profile_payload(
        {
            "STUD_ID": profile.STUD_ID,
            "fields": profile.fields,
            "metadata": profile.metadata,
            "text": profile.text,
        }
    )


def hash_semantic_profile_payload(payload: dict[str, Any]) -> str:
    stable_payload = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"), default=str)
    return sha256(stable_payload.encode("utf-8")).hexdigest()


def clean_profile_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, float):
        return f"{value:.2f}".rstrip("0").rstrip(".")
    return WHITESPACE_RE.sub(" ", str(value)).strip()


def semantic_profile_field_label(field_name: str) -> str:
    return FIELD_LABELS.get(field_name, field_name.replace("_", " ").title())


def is_private_semantic_profile_field(field_name: str) -> bool:
    normalized = field_name.upper()
    return normalized in PRIVATE_SEMANTIC_PROFILE_FIELDS or any(token in normalized for token in PRIVATE_FIELD_TOKENS)
