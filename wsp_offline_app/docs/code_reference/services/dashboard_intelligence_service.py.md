# `services/dashboard_intelligence_service.py`

[Open source](../../../services/dashboard_intelligence_service.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Builds the placement-focused dashboard model, faculty mappings, worklists, comparison signals, data-quality views, and chart-ready summaries.

## File facts

- **Type:** `.py`
- **Size:** 758 lines
- **Layer:** `services`
- **Python module:** `services.dashboard_intelligence_service`

## Dependencies and integration

- `__future__`
- `collections`
- `database.models`
- `services.analytics_service`
- `services.preferred_work_grouping_service`
- `services.technical_skill_grouping_service`
- `statistics`
- `typing`

### Referenced by

- `app/web_app.py`
- `scripts/run_preferred_work_edge_case_audit.py`
- `tests/test_dashboard_intelligence_service.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 93 | function | `faculty_for_major(major)` | Implementation symbol. |
| 108 | function | `build_dashboard_intelligence(session, work_grouper, skill_grouper, faculty, major, class_year, enrollment, aid, attention, gpa_min, gpa_max)` | Implementation symbol. |
| 186 | function | `_matches(student, selection)` | Implementation symbol. |
| 215 | function | `_multi_values(raw, allowed)` | Implementation symbol. |
| 228 | function | `_metrics(students)` | Implementation symbol. |
| 286 | function | `_quality_metrics(students, inactive_count)` | Implementation symbol. |
| 303 | function | `_faculty_summary(students, population_total)` | Implementation symbol. |
| 342 | function | `_charts(students, preference_grouping, skill_grouping)` | Implementation symbol. |
| 472 | function | `_filter_options(students)` | Implementation symbol. |
| 502 | function | `_student_rows(students, preference_grouping, order, limit)` | Implementation symbol. |
| 549 | function | `_preference_grouping_summary(students, grouping)` | Implementation symbol. |
| 577 | function | `_technical_skill_grouping_summary(students, grouping)` | Implementation symbol. |
| 601 | function | `_insights(students, metrics, quality, faculty_summary)` | Implementation symbol. |
| 652 | function | `_selection_label(selection)` | Implementation symbol. |
| 669 | function | `_faculty_points(counts)` | Implementation symbol. |
| 677 | function | `_faculty_rate_points(students, predicate)` | Implementation symbol. |
| 694 | function | `_counter_points(counts, limit)` | Implementation symbol. |
| 701 | function | `_needs_attention(student)` | Implementation symbol. |
| 705 | function | `_attention_label(student)` | Implementation symbol. |
| 714 | function | `_profile_complete(student)` | Implementation symbol. |
| 729 | function | `_core_missing_count(student)` | Implementation symbol. |
| 744 | function | `_has_experience(student)` | Implementation symbol. |
| 748 | function | `_present(value)` | Implementation symbol. |
| 752 | function | `_label(value)` | Implementation symbol. |
| 756 | function | `_rate(value, total)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `services/dashboard_intelligence_service.py` when its services responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
