from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable

from services.semantic_service import clean_semantic_value, extract_json_payload


ChatRunner = Callable[[str, str | None], str]


@dataclass(frozen=True)
class ChatSearchIntent:
    original_query: str
    semantic_query: str
    hard_filters: dict[str, Any] = field(default_factory=dict)
    qwen_used: bool = False


QUERY_REWRITE_SYSTEM_PROMPT = (
    "Rewrite the user's work-study request into a clear semantic retrieval query. "
    "Extract only explicit hard filters. Return JSON with semantic_query and hard_filters."
)


def interpret_chat_search_request(query: str, *, chat_runner: ChatRunner | None = None) -> ChatSearchIntent:
    clean_query = clean_semantic_value(query)
    if not clean_query:
        raise ValueError("Chat search query cannot be empty")
    if chat_runner is None:
        return ChatSearchIntent(original_query=clean_query, semantic_query=clean_query)

    prompt = json.dumps(
        {
            "request": clean_query,
            "hard_filter_examples": ["CUM_GPA >= 3", "PROBATION = No", "FINANCIAL_AID = Yes", "MAJR_DESC = Computer Science"],
            "response_format": {"semantic_query": "clear retrieval query", "hard_filters": {}},
        },
        ensure_ascii=True,
        indent=2,
    )
    response = chat_runner(prompt, QUERY_REWRITE_SYSTEM_PROMPT)
    payload = json.loads(extract_json_payload(response))
    semantic_query = clean_semantic_value(payload.get("semantic_query")) or clean_query
    hard_filters = payload.get("hard_filters") if isinstance(payload.get("hard_filters"), dict) else {}
    return ChatSearchIntent(
        original_query=clean_query,
        semantic_query=semantic_query,
        hard_filters=hard_filters,
        qwen_used=True,
    )
