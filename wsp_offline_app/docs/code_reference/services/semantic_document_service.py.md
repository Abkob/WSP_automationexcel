# `services/semantic_document_service.py`

[Open source](../../../services/semantic_document_service.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Builds deterministic original-text semantic profiles and hashes from student fields used by local matching.

## File facts

- **Type:** `.py`
- **Size:** 201 lines
- **Layer:** `services`
- **Python module:** `services.semantic_document_service`

## Dependencies and integration

- `__future__`
- `database.models`
- `dataclasses`
- `hashlib`
- `json`
- `re`
- `typing`

### Referenced by

- `app/web_app.py`
- `scripts/audit_semantic_index.py`
- `scripts/run_bias_testbench.py`
- `services/explanation_service.py`
- `services/semantic_search_service.py`
- `tests/test_semantic_document_service.py`
- `tests/test_semantic_search_service.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 62 | class | `StudentSemanticProfile` | Implementation symbol. |
| 70 | function | `build_student_semantic_profile(student, include_private_fields, source_fields)` | Implementation symbol. |
| 99 | function | `build_student_semantic_profiles(students)` | Implementation symbol. |
| 108 | function | `collect_semantic_profile_fields(student, include_private_fields, source_fields)` | Implementation symbol. |
| 124 | function | `build_semantic_profile_metadata(student)` | Implementation symbol. |
| 137 | function | `format_student_semantic_profile(fields)` | Implementation symbol. |
| 162 | function | `append_profile_section(sections, title, fields, field_names)` | Implementation symbol. |
| 168 | function | `hash_semantic_profile(profile)` | Implementation symbol. |
| 179 | function | `hash_semantic_profile_payload(payload)` | Implementation symbol. |
| 184 | function | `clean_profile_value(value)` | Implementation symbol. |
| 194 | function | `semantic_profile_field_label(field_name)` | Implementation symbol. |
| 198 | function | `is_private_semantic_profile_field(field_name)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `services/semantic_document_service.py` when its services responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
