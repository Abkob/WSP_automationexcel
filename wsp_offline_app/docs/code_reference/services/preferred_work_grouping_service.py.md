# `services/preferred_work_grouping_service.py`

[Open source](../../../services/preferred_work_grouping_service.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Groups free-text work preferences into reviewed, flexible, emerging, or needs-review topics while preserving original responses.

## File facts

- **Type:** `.py`
- **Size:** 431 lines
- **Layer:** `services`
- **Python module:** `services.preferred_work_grouping_service`

## Dependencies and integration

- `__future__`
- `config`
- `dataclasses`
- `functools`
- `hashlib`
- `numpy`
- `services.analytics_service`
- `services.embedding_service`
- `threading`
- `typing`

### Referenced by

- `app/web_app.py`
- `scripts/run_preferred_work_edge_case_audit.py`
- `services/dashboard_intelligence_service.py`
- `tests/test_dashboard_intelligence_service.py`
- `tests/test_preferred_work_grouping_service.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 17 | class | `WorkField` | Implementation symbol. |
| 158 | class | `PreferredWorkAssignment` | Implementation symbol. |
| 170 | class | `PreferredWorkGrouping` | Implementation symbol. |
| 180 | class | `PreferredWorkGrouper` | Groups free-text work preferences without changing their original text. |
| 371 | function | `normalized_preference_key(value)` | Implementation symbol. |
| 375 | function | `is_flexible_preference(key)` | Implementation symbol. |
| 390 | function | `is_uncertain_preference(key)` | Implementation symbol. |
| 395 | function | `flexible_assignment()` | Implementation symbol. |
| 407 | function | `review_assignment(method)` | Implementation symbol. |
| 419 | function | `ungrouped_preferences(values)` | Implementation symbol. |
| 429 | function | `get_default_preferred_work_grouper(settings)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `services/preferred_work_grouping_service.py` when its services responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
