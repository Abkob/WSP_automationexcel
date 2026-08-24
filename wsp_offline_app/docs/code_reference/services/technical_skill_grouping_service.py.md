# `services/technical_skill_grouping_service.py`

[Open source](../../../services/technical_skill_grouping_service.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Splits and semantically groups rough technical-skill text into stable, emerging, or unverified topics without rewriting source data.

## File facts

- **Type:** `.py`
- **Size:** 307 lines
- **Layer:** `services`
- **Python module:** `services.technical_skill_grouping_service`

## Dependencies and integration

- `__future__`
- `collections`
- `config`
- `dataclasses`
- `functools`
- `hashlib`
- `numpy`
- `re`
- `services.analytics_service`
- `services.embedding_service`
- `threading`
- `typing`

### Referenced by

- `app/web_app.py`
- `scripts/run_preferred_work_edge_case_audit.py`
- `services/dashboard_intelligence_service.py`
- `tests/test_dashboard_intelligence_service.py`
- `tests/test_technical_skill_grouping_service.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 19 | class | `SkillTopic` | Implementation symbol. |
| 53 | class | `TechnicalSkillAssignment` | Implementation symbol. |
| 64 | class | `TechnicalSkillGrouping` | Implementation symbol. |
| 84 | class | `TechnicalSkillGrouper` | Builds technical-skill topics from rough text across the student population. |
| 253 | function | `normalized_skill_key(value)` | Implementation symbol. |
| 257 | function | `is_uncertain_skill(key)` | Implementation symbol. |
| 262 | function | `is_non_skill_marker(key)` | Implementation symbol. |
| 266 | function | `topic_assignment(topic, method, confidence)` | Implementation symbol. |
| 282 | function | `review_assignment(method, confidence)` | Implementation symbol. |
| 293 | function | `ungrouped_technical_skills(values)` | Implementation symbol. |
| 305 | function | `get_default_technical_skill_grouper(settings)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `services/technical_skill_grouping_service.py` when its services responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
