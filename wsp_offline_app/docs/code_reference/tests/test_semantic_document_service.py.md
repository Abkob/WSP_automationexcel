# `tests/test_semantic_document_service.py`

[Open source](../../../tests/test_semantic_document_service.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides regression coverage for semantic document service, including expected success paths, validation rules, and failure behavior.

## File facts

- **Type:** `.py`
- **Size:** 86 lines
- **Layer:** `tests`
- **Python module:** `tests.test_semantic_document_service`

## Dependencies and integration

- `__future__`
- `database.models`
- `services.semantic_document_service`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 11 | function | `test_student_semantic_profile_contains_work_study_sections()` | Implementation symbol. |
| 35 | function | `test_semantic_profile_preserves_unique_original_wording_not_dashboard_topics()` | Implementation symbol. |
| 54 | function | `test_semantic_profile_excludes_private_contact_fields_by_default()` | Implementation symbol. |
| 72 | function | `test_semantic_profile_hash_is_stable_and_changes_when_profile_changes()` | Implementation symbol. |
| 81 | function | `test_private_semantic_profile_field_detection_catches_contact_like_names()` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `tests/test_semantic_document_service.py` when its tests responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
