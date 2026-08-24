# `tests/test_technical_skill_grouping_service.py`

[Open source](../../../tests/test_technical_skill_grouping_service.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides regression coverage for technical skill grouping service, including expected success paths, validation rules, and failure behavior.

## File facts

- **Type:** `.py`
- **Size:** 102 lines
- **Layer:** `tests`
- **Python module:** `tests.test_technical_skill_grouping_service`

## Dependencies and integration

- `__future__`
- `numpy`
- `services.technical_skill_grouping_service`
- `typing`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 10 | class | `SkillMeaningEmbeddingModel` | Implementation symbol. |
| 33 | function | `test_skills_are_split_and_grouped_semantically_between_students()` | Implementation symbol. |
| 58 | function | `test_same_unfamiliar_skill_repeated_by_two_students_creates_a_topic()` | Implementation symbol. |
| 69 | function | `test_one_student_cannot_create_a_dynamic_topic_by_repeating_it()` | Implementation symbol. |
| 80 | function | `test_known_aliases_are_stable_without_semantic_discovery()` | Implementation symbol. |
| 91 | function | `test_repeated_import_markers_never_become_skill_topics()` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `tests/test_technical_skill_grouping_service.py` when its tests responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
