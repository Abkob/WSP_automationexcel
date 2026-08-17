from __future__ import annotations

from database.models import StudentCurrent
from services.semantic_document_service import (
    build_student_semantic_profile,
    hash_semantic_profile,
    is_private_semantic_profile_field,
)


def test_student_semantic_profile_contains_work_study_sections() -> None:
    profile = build_student_semantic_profile(
        StudentCurrent(
            STUD_ID="1001",
            MAJR_DESC="Computer Science",
            CLAS_DESC="Junior",
            CUM_GPA=3.71,
            PROBATION=False,
            WSP_TECHNICAL_SKILLS="Excel, Python, dashboard reporting",
            WSP_PREFERRED_TYPE_OF_WORK="Office data entry and spreadsheet cleanup",
            WSP_ORGANIZATIONAL_SKILLS="Careful filing and deadline tracking",
        )
    )

    assert profile.STUD_ID == "1001"
    assert "Student profile for work-study matching" in profile.text
    assert "Academic:" in profile.text
    assert "Skills:" in profile.text
    assert "Excel, Python" in profile.text
    assert profile.metadata["major"] == "Computer Science"
    assert profile.metadata["probation"] is False
    assert profile.document_hash == hash_semantic_profile(profile)


def test_semantic_profile_preserves_unique_original_wording_not_dashboard_topics() -> None:
    unique_skills = "pyhton automtion for turtle sensor logs v2"
    unique_preference = "night-shift marine drone calibration near the coast"
    profile = build_student_semantic_profile(
        StudentCurrent(
            STUD_ID="UNIQUE-1",
            WSP_TECHNICAL_SKILLS=unique_skills,
            WSP_PREFERRED_TYPE_OF_WORK=unique_preference,
        )
    )

    assert profile.fields["WSP_TECHNICAL_SKILLS"] == unique_skills
    assert profile.fields["WSP_PREFERRED_TYPE_OF_WORK"] == unique_preference
    assert unique_skills in profile.text
    assert unique_preference in profile.text
    assert "Emerging ·" not in profile.text
    assert "Unverified / Needs Review" not in profile.text


def test_semantic_profile_excludes_private_contact_fields_by_default() -> None:
    profile = build_student_semantic_profile(
        StudentCurrent(
            STUD_ID="1001",
            STUD_NAME="Private Name",
            STUD_EMAIL="student@example.test",
            MOBILE_NBR="70123456",
            WSP_TECHNICAL_SKILLS="Excel",
        ),
        source_fields=("STUD_NAME", "STUD_EMAIL", "MOBILE_NBR", "WSP_TECHNICAL_SKILLS"),
    )

    assert "Private Name" not in profile.text
    assert "student@example.test" not in profile.text
    assert "70123456" not in profile.text
    assert "Excel" in profile.text


def test_semantic_profile_hash_is_stable_and_changes_when_profile_changes() -> None:
    first = build_student_semantic_profile(StudentCurrent(STUD_ID="1001", WSP_TECHNICAL_SKILLS="Excel"))
    same = build_student_semantic_profile(StudentCurrent(STUD_ID="1001", WSP_TECHNICAL_SKILLS="Excel"))
    changed = build_student_semantic_profile(StudentCurrent(STUD_ID="1001", WSP_TECHNICAL_SKILLS="Excel, SQL"))

    assert first.document_hash == same.document_hash
    assert first.document_hash != changed.document_hash


def test_private_semantic_profile_field_detection_catches_contact_like_names() -> None:
    assert is_private_semantic_profile_field("STUD_EMAIL")
    assert is_private_semantic_profile_field("PARENT_PHONE")
    assert is_private_semantic_profile_field("CONTACT_NAME")
    assert not is_private_semantic_profile_field("WSP_TECHNICAL_SKILLS")
