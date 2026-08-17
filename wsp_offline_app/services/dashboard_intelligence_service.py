from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean
from typing import Any, Iterable

from database.models import StudentCurrent
from services.analytics_service import split_subjective_terms
from services.preferred_work_grouping_service import (
    PreferredWorkGrouper,
    PreferredWorkGrouping,
    ungrouped_preferences,
)
from services.technical_skill_grouping_service import (
    TechnicalSkillGrouper,
    TechnicalSkillGrouping,
    ungrouped_technical_skills,
)


FACULTIES: tuple[dict[str, Any], ...] = (
    {
        "code": "FAS",
        "name": "Faculty of Arts and Sciences",
        "short_name": "Arts & Sciences",
        "color": "#7A1831",
        "majors": (
            "Psychology",
            "Political Science",
            "Computer Science",
            "Chemistry",
            "Biology",
            "English Literature",
        ),
    },
    {
        "code": "OSB",
        "name": "Suliman S. Olayan School of Business",
        "short_name": "Business",
        "color": "#1F5A7A",
        "majors": ("Business Administration", "Accounting", "Finance", "Marketing"),
    },
    {
        "code": "MSFEA",
        "name": "Maroun Semaan Faculty of Engineering and Architecture",
        "short_name": "Engineering & Architecture",
        "color": "#B86B1F",
        "majors": ("Architecture", "Electrical Engineering", "Graphic Design"),
    },
    {
        "code": "FHS",
        "name": "Faculty of Health Sciences",
        "short_name": "Health Sciences",
        "color": "#0F766E",
        "majors": ("Public Health",),
    },
    {
        "code": "HSON",
        "name": "Rafic Hariri School of Nursing",
        "short_name": "Nursing",
        "color": "#4B5AA7",
        "majors": ("Nursing",),
    },
    {
        "code": "FAFS",
        "name": "Faculty of Agricultural and Food Sciences",
        "short_name": "Agricultural & Food Sciences",
        "color": "#5D7A3C",
        "majors": (),
    },
    {
        "code": "FM",
        "name": "Faculty of Medicine",
        "short_name": "Medicine",
        "color": "#74536B",
        "majors": (),
    },
)

FACULTY_BY_CODE = {faculty["code"]: faculty for faculty in FACULTIES}
FACULTY_BY_MAJOR = {
    major.casefold(): faculty
    for faculty in FACULTIES
    for major in faculty["majors"]
}
MAJOR_ALIASES = {
    "political studies": "Political Science",
    "electrical and computer engineering": "Electrical Engineering",
    "bachelor of science in nursing": "Nursing",
}


def faculty_for_major(major: str | None) -> dict[str, Any]:
    clean_major = str(major or "").strip()
    alias = MAJOR_ALIASES.get(clean_major.casefold(), clean_major)
    return FACULTY_BY_MAJOR.get(
        alias.casefold(),
        {
            "code": "UNMAPPED",
            "name": "Unmapped faculty",
            "short_name": "Unmapped",
            "color": "#64748B",
            "majors": (),
        },
    )


def build_dashboard_intelligence(
    session,
    *,
    work_grouper: PreferredWorkGrouper | None = None,
    skill_grouper: TechnicalSkillGrouper | None = None,
    faculty: str = "",
    major: str = "",
    class_year: str = "",
    enrollment: str = "any",
    aid: str = "any",
    attention: str = "any",
    gpa_min: float | None = None,
    gpa_max: float | None = None,
) -> dict[str, Any]:
    all_active = tuple(
        session.query(StudentCurrent)
        .filter(StudentCurrent.missing_from_latest_import.is_(False))
        .all()
    )
    selection = {
        "faculty": _multi_values(faculty, allowed=set(FACULTY_BY_CODE)),
        "major": _multi_values(major),
        "class_year": _multi_values(class_year),
        "enrollment": enrollment if enrollment in {"any", "enrolled", "registered", "not_registered"} else "any",
        "aid": aid if aid in {"any", "yes", "no"} else "any",
        "attention": attention if attention in {"any", "yes", "no"} else "any",
        "gpa_min": gpa_min,
        "gpa_max": gpa_max,
    }
    filtered = tuple(student for student in all_active if _matches(student, selection))
    total = len(filtered)

    faculty_scope_selection = {**selection, "faculty": ()}
    if selection["faculty"]:
        faculty_scope_selection["major"] = ()
    faculty_scope = tuple(student for student in all_active if _matches(student, faculty_scope_selection))
    faculty_summary = _faculty_summary(faculty_scope, population_total=len(faculty_scope))
    selected_faculty_summary = _faculty_summary(filtered, population_total=total)
    metrics = _metrics(filtered)
    quality = _quality_metrics(filtered, session.query(StudentCurrent).count() - len(all_active))
    # Discover fields against the complete active population so cluster membership
    # remains stable while faculty/class filters reshape the dashboard.
    preference_values = [student.WSP_PREFERRED_TYPE_OF_WORK for student in all_active if _present(student.WSP_PREFERRED_TYPE_OF_WORK)]
    preference_grouping = work_grouper.group(preference_values) if work_grouper else ungrouped_preferences(preference_values)
    skill_values = [student.WSP_TECHNICAL_SKILLS for student in all_active if _present(student.WSP_TECHNICAL_SKILLS)]
    skill_grouping = skill_grouper.group(skill_values) if skill_grouper else ungrouped_technical_skills(skill_values)
    charts = _charts(filtered, preference_grouping, skill_grouping)
    options = _filter_options(all_active)
    students = _student_rows(filtered, preference_grouping=preference_grouping, order="candidate")
    workstudy_students = _student_rows(filtered, preference_grouping=preference_grouping, order="workstudy")
    support_students = _student_rows(filtered, preference_grouping=preference_grouping, order="support")
    quality_candidates = tuple(
        student
        for student in filtered
        if _core_missing_count(student) > 0 or faculty_for_major(student.MAJR_DESC)["code"] == "UNMAPPED"
    )
    quality_students = _student_rows(quality_candidates, preference_grouping=preference_grouping, order="quality")

    return {
        "selection": selection,
        "selection_label": _selection_label(selection),
        "filter_options": options,
        "faculty_summary": faculty_summary,
        "metrics": metrics,
        "quality": quality,
        "charts": charts,
        "preferred_work_grouping": _preference_grouping_summary(filtered, preference_grouping),
        "technical_skill_grouping": _technical_skill_grouping_summary(filtered, skill_grouping),
        "insights": _insights(filtered, metrics, quality, selected_faculty_summary),
        "students": students,
        "candidate_students": students,
        "workstudy_students": workstudy_students,
        "support_students": support_students,
        "quality_students": quality_students,
        "total_matches": total,
    }


def _matches(student: StudentCurrent, selection: dict[str, Any]) -> bool:
    if selection["faculty"] and faculty_for_major(student.MAJR_DESC)["code"] not in selection["faculty"]:
        return False
    if selection["major"] and (student.MAJR_DESC or "") not in selection["major"]:
        return False
    if selection["class_year"] and (student.CLAS_DESC or "") not in selection["class_year"]:
        return False
    if selection["enrollment"] == "enrolled" and student.ENROLLED_IND is not True:
        return False
    if selection["enrollment"] == "registered" and student.REGISTERED_IND is not True:
        return False
    if selection["enrollment"] == "not_registered" and student.REGISTERED_IND is True:
        return False
    if selection["aid"] == "yes" and student.FINANCIAL_AID is not True:
        return False
    if selection["aid"] == "no" and student.FINANCIAL_AID is not False:
        return False
    needs_attention = _needs_attention(student)
    if selection["attention"] == "yes" and not needs_attention:
        return False
    if selection["attention"] == "no" and needs_attention:
        return False
    if selection["gpa_min"] is not None and (student.CUM_GPA is None or student.CUM_GPA < selection["gpa_min"]):
        return False
    if selection["gpa_max"] is not None and (student.CUM_GPA is None or student.CUM_GPA > selection["gpa_max"]):
        return False
    return True


def _multi_values(raw: Any, *, allowed: set[str] | None = None) -> tuple[str, ...]:
    if raw is None:
        return ()
    source = raw if isinstance(raw, (list, tuple, set)) else str(raw).split(",")
    values: list[str] = []
    for item in source:
        value = str(item or "").strip()
        if not value or (allowed is not None and value not in allowed) or value in values:
            continue
        values.append(value)
    return tuple(values)


def _metrics(students: tuple[StudentCurrent, ...]) -> dict[str, Any]:
    total = len(students)
    gpas = [float(student.CUM_GPA) for student in students if student.CUM_GPA is not None]
    credits = [float(student.TOTAL_CREDIT_HOURS) for student in students if student.TOTAL_CREDIT_HOURS is not None]
    probation = sum(student.PROBATION is True for student in students)
    warnings = sum(student.DEANS_WARNING is True or student.DEAN_WARN is True for student in students)
    attention = sum(_needs_attention(student) for student in students)
    aid = sum(student.FINANCIAL_AID is True for student in students)
    registered = sum(student.REGISTERED_IND is True for student in students)
    enrolled = sum(student.ENROLLED_IND is True for student in students)
    complete = sum(_profile_complete(student) for student in students)
    skills_count = sum(_present(student.WSP_TECHNICAL_SKILLS) for student in students)
    work_preference_count = sum(_present(student.WSP_PREFERRED_TYPE_OF_WORK) for student in students)
    experience_count = sum(_present(student.WSP_PREV_WORK) or _present(student.WSP_PREVIOUS_TYPE_OF_WORK) for student in students)
    language_count = sum(_present(student.WSP_SPOKEN_LANGUAGES) or _present(student.WSP_WRITTEN_LANGUAGES) for student in students)
    below_2_count = sum(student.CUM_GPA is not None and student.CUM_GPA < 2 for student in students)
    missing_core_count = sum(not _profile_complete(student) for student in students)
    aid_attention_count = sum(student.FINANCIAL_AID is True and _needs_attention(student) for student in students)
    dorm_count = sum(student.DORMS is True for student in students)
    aid_dorm_count = sum(student.FINANCIAL_AID is True and student.DORMS is True for student in students)
    return {
        "total_students": total,
        "average_gpa": round(mean(gpas), 2) if gpas else None,
        "average_credits": round(mean(credits), 1) if credits else None,
        "probation_count": probation,
        "dean_warning_count": warnings,
        "attention_count": attention,
        "attention_rate": _rate(attention, total),
        "financial_aid_count": aid,
        "financial_aid_rate": _rate(aid, total),
        "registered_count": registered,
        "registered_rate": _rate(registered, total),
        "enrolled_count": enrolled,
        "enrolled_rate": _rate(enrolled, total),
        "profile_complete_count": complete,
        "profile_complete_rate": _rate(complete, total),
        "skills_count": skills_count,
        "skills_rate": _rate(skills_count, total),
        "work_preference_count": work_preference_count,
        "work_preference_rate": _rate(work_preference_count, total),
        "experience_count": experience_count,
        "experience_rate": _rate(experience_count, total),
        "language_count": language_count,
        "language_rate": _rate(language_count, total),
        "below_2_count": below_2_count,
        "below_2_rate": _rate(below_2_count, total),
        "missing_core_count": missing_core_count,
        "missing_core_rate": _rate(missing_core_count, total),
        "aid_attention_count": aid_attention_count,
        "aid_attention_rate": _rate(aid_attention_count, aid),
        "dorm_count": dorm_count,
        "dorm_rate": _rate(dorm_count, total),
        "aid_dorm_count": aid_dorm_count,
        "major_count": len({student.MAJR_DESC for student in students if _present(student.MAJR_DESC)}),
        "class_count": len({student.CLAS_DESC for student in students if _present(student.CLAS_DESC)}),
    }


def _quality_metrics(students: tuple[StudentCurrent, ...], inactive_count: int) -> dict[str, Any]:
    total = len(students)
    result = {
        "missing_email": sum(not _present(student.STUD_EMAIL) for student in students),
        "missing_mobile": sum(not _present(student.MOBILE_NBR) for student in students),
        "missing_major": sum(not _present(student.MAJR_DESC) for student in students),
        "missing_skills": sum(not _present(student.WSP_TECHNICAL_SKILLS) for student in students),
        "missing_work_preference": sum(not _present(student.WSP_PREFERRED_TYPE_OF_WORK) for student in students),
        "unmapped_faculty": sum(faculty_for_major(student.MAJR_DESC)["code"] == "UNMAPPED" for student in students),
        "inactive_records": max(0, inactive_count),
    }
    result["missing_any_core"] = sum(not _profile_complete(student) for student in students)
    result["complete_records"] = total - result["missing_any_core"]
    result["complete_rate"] = _rate(result["complete_records"], total)
    return result


def _faculty_summary(students: tuple[StudentCurrent, ...], *, population_total: int) -> list[dict[str, Any]]:
    grouped: dict[str, list[StudentCurrent]] = defaultdict(list)
    for student in students:
        grouped[faculty_for_major(student.MAJR_DESC)["code"]].append(student)

    summary = []
    definitions = list(FACULTIES)
    if grouped.get("UNMAPPED"):
        definitions.append(faculty_for_major(None))
    for definition in definitions:
        members = grouped.get(definition["code"], [])
        gpas = [float(student.CUM_GPA) for student in members if student.CUM_GPA is not None]
        aid_count = sum(student.FINANCIAL_AID is True for student in members)
        attention_count = sum(_needs_attention(student) for student in members)
        experience_count = sum(_has_experience(student) for student in members)
        dorm_count = sum(student.DORMS is True for student in members)
        summary.append(
            {
                "code": definition["code"],
                "name": definition["name"],
                "short_name": definition["short_name"],
                "color": definition["color"],
                "count": len(members),
                "share": _rate(len(members), population_total),
                "average_gpa": round(mean(gpas), 2) if gpas else None,
                "aid_count": aid_count,
                "aid_rate": _rate(aid_count, len(members)),
                "attention_count": attention_count,
                "attention_rate": _rate(attention_count, len(members)),
                "experience_count": experience_count,
                "experience_rate": _rate(experience_count, len(members)),
                "dorm_count": dorm_count,
                "dorm_rate": _rate(dorm_count, len(members)),
                "major_count": len({student.MAJR_DESC for student in members if _present(student.MAJR_DESC)}),
            }
        )
    return summary


def _charts(
    students: tuple[StudentCurrent, ...],
    preference_grouping: PreferredWorkGrouping,
    skill_grouping: TechnicalSkillGrouping,
) -> dict[str, list[dict[str, Any]]]:
    faculty_counts = Counter(faculty_for_major(student.MAJR_DESC)["code"] for student in students)
    major_counts = Counter(_label(student.MAJR_DESC) for student in students)
    class_counts = Counter(_label(student.CLAS_DESC) for student in students)
    attention_counts = Counter(faculty_for_major(student.MAJR_DESC)["code"] for student in students if _needs_attention(student))
    gpa_bins = Counter({"0.00–1.99": 0, "2.00–2.49": 0, "2.50–2.99": 0, "3.00–3.49": 0, "3.50–4.00": 0})
    for student in students:
        if student.CUM_GPA is None:
            continue
        if student.CUM_GPA < 2:
            gpa_bins["0.00–1.99"] += 1
        elif student.CUM_GPA < 2.5:
            gpa_bins["2.00–2.49"] += 1
        elif student.CUM_GPA < 3:
            gpa_bins["2.50–2.99"] += 1
        elif student.CUM_GPA < 3.5:
            gpa_bins["3.00–3.49"] += 1
        else:
            gpa_bins["3.50–4.00"] += 1

    probation_only = sum(student.PROBATION is True and not (student.DEANS_WARNING is True or student.DEAN_WARN is True) for student in students)
    warning_only = sum(student.PROBATION is not True and (student.DEANS_WARNING is True or student.DEAN_WARN is True) for student in students)
    both_alerts = sum(student.PROBATION is True and (student.DEANS_WARNING is True or student.DEAN_WARN is True) for student in students)

    class_groups: dict[str, list[StudentCurrent]] = defaultdict(list)
    for student in students:
        class_groups[_label(student.CLAS_DESC)].append(student)
    average_gpa_by_class = []
    aid_rate_by_class = []
    for label, members in class_groups.items():
        class_gpas = [float(member.CUM_GPA) for member in members if member.CUM_GPA is not None]
        if class_gpas:
            average_gpa_by_class.append({"label": label, "value": round(mean(class_gpas), 2), "detail": f"{len(class_gpas)} GPA records"})
        aid_count = sum(member.FINANCIAL_AID is True for member in members)
        aid_rate_by_class.append({"label": label, "value": _rate(aid_count, len(members)), "detail": f"{aid_count} of {len(members)} students"})
    average_gpa_by_class.sort(key=lambda point: (-point["value"], point["label"]))
    aid_rate_by_class.sort(key=lambda point: (-point["value"], point["label"]))

    field_checks = (
        ("Student email", lambda student: _present(student.STUD_EMAIL)),
        ("Mobile number", lambda student: _present(student.MOBILE_NBR)),
        ("Major", lambda student: _present(student.MAJR_DESC)),
        ("Technical skills", lambda student: _present(student.WSP_TECHNICAL_SKILLS)),
        ("Work preference", lambda student: _present(student.WSP_PREFERRED_TYPE_OF_WORK)),
    )
    data_completeness = []
    for label, check in field_checks:
        present_count = sum(check(student) for student in students)
        data_completeness.append({"label": label, "value": _rate(present_count, len(students)), "detail": f"{present_count} of {len(students)} complete"})
    data_completeness.sort(key=lambda point: (point["value"], point["label"]))

    skill_counts: Counter[str] = Counter()
    skill_colors: dict[str, str] = {}
    skill_variants: dict[str, set[str]] = defaultdict(set)
    skill_assignment_by_code = {
        assignment.topic_code: assignment
        for assignment in skill_grouping.assignments.values()
    }
    for student in students:
        student_topics: set[str] = set()
        for raw_term in split_subjective_terms(student.WSP_TECHNICAL_SKILLS, split_on_and=True):
            assignment = skill_grouping.for_term(raw_term)
            if assignment is None:
                continue
            if assignment.needs_review:
                continue
            student_topics.add(assignment.topic_code)
            skill_colors[assignment.topic_label] = assignment.color
            skill_variants[assignment.topic_label].add(_label(raw_term))
        for topic_code in student_topics:
            assignment = skill_assignment_by_code.get(topic_code)
            if assignment:
                skill_counts[assignment.topic_label] += 1
    skill_points = [
        {
            "label": label,
            "value": count,
            "color": skill_colors[label],
            "detail": f"{len(skill_variants[label])} answer variant{'s' if len(skill_variants[label]) != 1 else ''}",
        }
        for label, count in sorted(skill_counts.items(), key=lambda item: (-item[1], item[0]))
    ]
    work_counts: Counter[str] = Counter()
    work_colors: dict[str, str] = {}
    work_variants: dict[str, set[str]] = defaultdict(set)
    for student in students:
        if not _present(student.WSP_PREFERRED_TYPE_OF_WORK):
            continue
        assignment = preference_grouping.for_value(student.WSP_PREFERRED_TYPE_OF_WORK)
        if assignment is None:
            continue
        work_counts[assignment.field_label] += 1
        work_colors[assignment.field_label] = assignment.color
        work_variants[assignment.field_label].add(_label(student.WSP_PREFERRED_TYPE_OF_WORK))
    work_points = [
        {
            "label": label,
            "value": count,
            "color": work_colors[label],
            "detail": f"{len(work_variants[label])} distinct answer{'s' if len(work_variants[label]) != 1 else ''}",
        }
        for label, count in sorted(work_counts.items(), key=lambda item: (-item[1], item[0]))
    ]
    return {
        "students_by_faculty": _faculty_points(faculty_counts),
        "students_by_major": _counter_points(major_counts),
        "students_by_class": _counter_points(class_counts),
        "gpa_distribution": [{"label": label, "value": value} for label, value in gpa_bins.items()],
        "attention_by_faculty": _faculty_points(attention_counts),
        "attention_rate_by_faculty": _faculty_rate_points(students, _needs_attention),
        "aid_rate_by_faculty": _faculty_rate_points(students, lambda student: student.FINANCIAL_AID is True),
        "dorm_rate_by_faculty": _faculty_rate_points(students, lambda student: student.DORMS is True),
        "experience_rate_by_faculty": _faculty_rate_points(students, _has_experience),
        "average_gpa_by_class": average_gpa_by_class,
        "aid_rate_by_class": aid_rate_by_class,
        "attention_breakdown": [
            {"label": "Both flags", "value": both_alerts, "detail": "Probation and dean warning"},
            {"label": "Probation only", "value": probation_only, "detail": "Probation without dean warning"},
            {"label": "Warning only", "value": warning_only, "detail": "Dean warning without probation"},
        ],
        "data_completeness": data_completeness,
        "technical_skills": skill_points[:10],
        "work_preferences": work_points,
    }


def _filter_options(students: tuple[StudentCurrent, ...]) -> dict[str, Any]:
    faculty_counts = Counter(faculty_for_major(student.MAJR_DESC)["code"] for student in students)
    faculties = []
    for definition in FACULTIES:
        if faculty_counts[definition["code"]] == 0:
            continue
        faculties.append(
            {
                "code": definition["code"],
                "name": definition["name"],
                "short_name": definition["short_name"],
                "color": definition["color"],
                "count": faculty_counts[definition["code"]],
                "majors": sorted(
                    {
                        student.MAJR_DESC
                        for student in students
                        if _present(student.MAJR_DESC) and faculty_for_major(student.MAJR_DESC)["code"] == definition["code"]
                    }
                ),
            }
        )
    return {
        "faculties": faculties,
        "majors": sorted({_label(student.MAJR_DESC) for student in students if _present(student.MAJR_DESC)}),
        "classes": sorted({_label(student.CLAS_DESC) for student in students if _present(student.CLAS_DESC)}),
        "terms": sorted({_label(student.ENRL_TERM) for student in students if _present(student.ENRL_TERM)}, reverse=True),
    }


def _student_rows(
    students: tuple[StudentCurrent, ...],
    *,
    preference_grouping: PreferredWorkGrouping,
    order: str = "priority",
    limit: int = 10,
) -> list[dict[str, Any]]:
    def sort_key(student: StudentCurrent) -> tuple[Any, ...]:
        if order == "candidate":
            return (student.STUD_NAME or "",)
        if order == "workstudy":
            return (student.STUD_NAME or "",)
        if order == "support":
            return (not (student.FINANCIAL_AID is True), not (student.DORMS is True), student.STUD_NAME or "")
        if order == "quality":
            return (-_core_missing_count(student), student.STUD_NAME or "")
        return (not _needs_attention(student), student.CUM_GPA if student.CUM_GPA is not None else 5, student.STUD_NAME or "")

    ordered = sorted(students, key=sort_key)
    rows: list[dict[str, Any]] = []
    for student in ordered[:limit]:
        assignment = preference_grouping.for_value(student.WSP_PREFERRED_TYPE_OF_WORK)
        rows.append({
            "student_id": student.STUD_ID,
            "name": student.STUD_NAME or "Unnamed student",
            "faculty": faculty_for_major(student.MAJR_DESC)["code"],
            "faculty_color": faculty_for_major(student.MAJR_DESC)["color"],
            "major": student.MAJR_DESC or "Not provided",
            "class_year": student.CLAS_DESC or "Not provided",
            "gpa": student.CUM_GPA,
            "registered": student.REGISTERED_IND,
            "financial_aid": student.FINANCIAL_AID,
            "dorms": student.DORMS,
            "attention": _needs_attention(student),
            "attention_label": _attention_label(student),
            "work_preference": student.WSP_PREFERRED_TYPE_OF_WORK or "Not provided",
            "work_preference_group": assignment.field_label if assignment else "Not provided",
            "work_preference_group_color": assignment.color if assignment else "#64748B",
            "work_preference_confidence": assignment.confidence if assignment else None,
            "work_preference_needs_review": assignment.needs_review if assignment else False,
            "work_preference_is_emerging": assignment.is_emerging if assignment else False,
            "has_experience": _has_experience(student),
            "core_missing_count": _core_missing_count(student),
        })
    return rows


def _preference_grouping_summary(
    students: tuple[StudentCurrent, ...],
    grouping: PreferredWorkGrouping,
) -> dict[str, Any]:
    assignments = [
        grouping.for_value(student.WSP_PREFERRED_TYPE_OF_WORK)
        for student in students
        if _present(student.WSP_PREFERRED_TYPE_OF_WORK)
    ]
    resolved = [assignment for assignment in assignments if assignment is not None]
    review_count = sum(assignment.needs_review for assignment in resolved)
    flexible_count = sum(assignment.field_code == "flexible" for assignment in resolved)
    emerging_codes = {assignment.field_code for assignment in resolved if assignment.is_emerging}
    emerging_count = sum(assignment.is_emerging for assignment in resolved)
    return {
        "method": "offline_embeddings" if grouping.model_available else "review_fallback",
        "model": grouping.model_name,
        "original_text_preserved": True,
        "preference_count": len(resolved),
        "assigned_count": len(resolved) - review_count,
        "flexible_count": flexible_count,
        "emerging_count": emerging_count,
        "emerging_field_count": len(emerging_codes),
        "review_count": review_count,
        "review_rate": _rate(review_count, len(resolved)),
    }


def _technical_skill_grouping_summary(
    students: tuple[StudentCurrent, ...],
    grouping: TechnicalSkillGrouping,
) -> dict[str, Any]:
    assignments = [
        assignment
        for student in students
        for assignment in grouping.assignments_for_value(student.WSP_TECHNICAL_SKILLS)
    ]
    review_count = sum(assignment.needs_review for assignment in assignments)
    emerging_codes = {assignment.topic_code for assignment in assignments if assignment.is_emerging}
    return {
        "method": "offline_embeddings" if grouping.model_available else "review_fallback",
        "model": grouping.model_name,
        "original_text_preserved": True,
        "skill_topic_mentions": len(assignments),
        "mapped_count": len(assignments) - review_count,
        "emerging_count": sum(assignment.is_emerging for assignment in assignments),
        "emerging_topic_count": len(emerging_codes),
        "review_count": review_count,
        "review_rate": _rate(review_count, len(assignments)),
    }


def _insights(
    students: tuple[StudentCurrent, ...],
    metrics: dict[str, Any],
    quality: dict[str, int],
    faculty_summary: list[dict[str, Any]],
) -> list[dict[str, str]]:
    total = len(students)
    if total == 0:
        return [{"tone": "neutral", "title": "No students match", "body": "Remove one or more filters to restore the dashboard population.", "action": "clear"}]

    populated_faculties = [item for item in faculty_summary if item["count"]]
    largest = max(populated_faculties, key=lambda item: item["count"], default=None)
    insights = []
    if largest:
        insights.append(
            {
                "tone": "aub",
                "title": f"{largest['code']} is the largest selected faculty",
                "body": f"{largest['count']:,} students represent {largest['share']:.1f}% of this view, across {largest['major_count']} major(s).",
                "action": f"faculty:{largest['code']}",
            }
        )
    insights.append(
        {
            "tone": "warn" if metrics["attention_count"] else "good",
            "title": f"{metrics['attention_count']:,} students need academic attention",
            "body": f"That is {metrics['attention_rate']:.1f}% of the selected population, based on probation or dean-warning flags.",
            "action": "attention:yes",
        }
    )
    incomplete = total - metrics["profile_complete_count"]
    insights.append(
        {
            "tone": "blue" if incomplete else "good",
            "title": f"{metrics['profile_complete_rate']:.1f}% profile completeness",
            "body": f"{incomplete:,} selected records are missing at least one core identity, contact, skill, or work-preference field.",
            "action": "tab:quality",
        }
    )
    if quality["unmapped_faculty"]:
        insights.append(
            {
                "tone": "danger",
                "title": f"{quality['unmapped_faculty']:,} majors need faculty mapping",
                "body": "These records are retained in an Unmapped group so they cannot silently enter the wrong faculty.",
                "action": "tab:quality",
            }
        )
    return insights[:4]


def _selection_label(selection: dict[str, Any]) -> str:
    parts = []
    if selection["faculty"]:
        parts.append(", ".join(selection["faculty"]))
    if selection["major"]:
        parts.append(", ".join(selection["major"]))
    if selection["class_year"]:
        parts.append(", ".join(selection["class_year"]))
    if selection["enrollment"] != "any":
        parts.append(selection["enrollment"].replace("_", " ").title())
    if selection["aid"] != "any":
        parts.append(f"Aid: {selection['aid'].title()}")
    if selection["attention"] != "any":
        parts.append(f"Attention: {selection['attention'].title()}")
    return " · ".join(parts) or "All current applicants"


def _faculty_points(counts: Counter[str]) -> list[dict[str, Any]]:
    points = []
    for code, value in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        definition = FACULTY_BY_CODE.get(code) or faculty_for_major(None)
        points.append({"label": code, "value": value, "color": definition["color"], "detail": definition["short_name"]})
    return points


def _faculty_rate_points(students: tuple[StudentCurrent, ...], predicate: Any) -> list[dict[str, Any]]:
    grouped: dict[str, list[StudentCurrent]] = defaultdict(list)
    for student in students:
        grouped[faculty_for_major(student.MAJR_DESC)["code"]].append(student)
    points = []
    for code, members in grouped.items():
        matching = sum(predicate(student) for student in members)
        definition = FACULTY_BY_CODE.get(code) or faculty_for_major(None)
        points.append({
            "label": code,
            "value": _rate(matching, len(members)),
            "color": definition["color"],
            "detail": f"{matching} of {len(members)} students",
        })
    return sorted(points, key=lambda point: (-point["value"], point["label"]))


def _counter_points(counts: Counter[str], *, limit: int | None = None) -> list[dict[str, Any]]:
    items = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    if limit:
        items = items[:limit]
    return [{"label": label, "value": value} for label, value in items]


def _needs_attention(student: StudentCurrent) -> bool:
    return student.PROBATION is True or student.DEANS_WARNING is True or student.DEAN_WARN is True


def _attention_label(student: StudentCurrent) -> str:
    labels = []
    if student.PROBATION is True:
        labels.append("Probation")
    if student.DEANS_WARNING is True or student.DEAN_WARN is True:
        labels.append("Dean warning")
    return " + ".join(labels) or "No alert"


def _profile_complete(student: StudentCurrent) -> bool:
    return all(
        _present(value)
        for value in (
            student.STUD_NAME,
            student.STUD_EMAIL,
            student.MOBILE_NBR,
            student.MAJR_DESC,
            student.CLAS_DESC,
            student.WSP_TECHNICAL_SKILLS,
            student.WSP_PREFERRED_TYPE_OF_WORK,
        )
    )


def _core_missing_count(student: StudentCurrent) -> int:
    return sum(
        not _present(value)
        for value in (
            student.STUD_NAME,
            student.STUD_EMAIL,
            student.MOBILE_NBR,
            student.MAJR_DESC,
            student.CLAS_DESC,
            student.WSP_TECHNICAL_SKILLS,
            student.WSP_PREFERRED_TYPE_OF_WORK,
        )
    )


def _has_experience(student: StudentCurrent) -> bool:
    return bool(_present(student.WSP_PREV_WORK) or _present(student.WSP_PREVIOUS_TYPE_OF_WORK))


def _present(value: Any) -> bool:
    return value is not None and bool(str(value).strip())


def _label(value: Any) -> str:
    return str(value).strip() if _present(value) else "Unknown"


def _rate(value: int, total: int) -> float:
    return round((value / total) * 100, 1) if total else 0.0
