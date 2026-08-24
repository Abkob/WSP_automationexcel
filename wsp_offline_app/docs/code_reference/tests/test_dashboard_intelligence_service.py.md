# `tests/test_dashboard_intelligence_service.py`

[Open source](../../../tests/test_dashboard_intelligence_service.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides regression coverage for dashboard intelligence service, including expected success paths, validation rules, and failure behavior.

## File facts

- **Type:** `.py`
- **Size:** 266 lines
- **Layer:** `tests`
- **Python module:** `tests.test_dashboard_intelligence_service`

## Dependencies and integration

- `__future__`
- `database.db`
- `database.models`
- `numpy`
- `services.dashboard_intelligence_service`
- `services.preferred_work_grouping_service`
- `services.technical_skill_grouping_service`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 12 | class | `DashboardWorkEmbeddingModel` | Implementation symbol. |
| 32 | class | `DashboardSkillEmbeddingModel` | Implementation symbol. |
| 50 | function | `test_official_faculty_mapping_uses_major_not_unreliable_college_code()` | Implementation symbol. |
| 61 | function | `test_dashboard_intelligence_filters_and_summarizes_students(tmp_path)` | Implementation symbol. |
| 126 | function | `test_attention_filter_and_quality_metrics_are_transparent(tmp_path)` | Implementation symbol. |
| 148 | function | `test_dashboard_supports_multiple_values_per_category(tmp_path)` | Implementation symbol. |
| 175 | function | `test_previous_experience_remains_optional_candidate_context(tmp_path)` | Implementation symbol. |
| 199 | function | `test_emerging_work_field_is_discovered_from_full_population_before_filtering(tmp_path)` | Implementation symbol. |
| 233 | function | `test_dynamic_skill_topic_uses_cross_student_evidence_before_filtering(tmp_path)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `tests/test_dashboard_intelligence_service.py` when its tests responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
