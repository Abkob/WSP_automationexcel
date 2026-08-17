from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from services.semantic_document_service import StudentSemanticProfile, semantic_profile_field_label


EXPLANATION_FIELDS = (
    "WSP_PREFERRED_TYPE_OF_WORK",
    "WSP_TECHNICAL_SKILLS",
    "WSP_PREV_WORK",
    "WSP_PREVIOUS_TYPE_OF_WORK",
    "WSP_ORGANIZATIONAL_SKILLS",
    "WSP_INTERPERSONAL_SKILLS",
    "WSP_ADDITIONAL_SKILLS",
    "WSP_WRITTEN_LANGUAGES",
    "WSP_SPOKEN_LANGUAGES",
)


@dataclass(frozen=True)
class OriginalTextEvidence:
    field_name: str
    value: str
    similarity: float


def build_local_semantic_explanation(
    query: str,
    profile: StudentSemanticProfile,
    *,
    score: float,
    evidence: Iterable[OriginalTextEvidence] = (),
) -> str:
    ranked_evidence = tuple(evidence)
    if ranked_evidence:
        evidence_text = "; ".join(
            f'{semantic_profile_field_label(item.field_name)} “{truncate_explanation_text(item.value, max_length=82)}” ({item.similarity:.2f})'
            for item in ranked_evidence[:2]
        )
        return f"Embedding match {score:.2f}. Closest original evidence: {evidence_text}."

    field_summaries = []
    for field_name in EXPLANATION_FIELDS:
        value = profile.fields.get(field_name)
        if value:
            field_summaries.append(f"{semantic_profile_field_label(field_name)}: {truncate_explanation_text(value)}")
        if len(field_summaries) == 2:
            break
    if field_summaries:
        return f"Embedding match {score:.2f}. Original profile text: " + " ".join(field_summaries)
    return f"Embedding match {score:.2f} against the student's work-study profile."


def truncate_explanation_text(value: str, *, max_length: int = 140) -> str:
    clean_value = " ".join(str(value).split())
    if len(clean_value) <= max_length:
        return clean_value
    return f"{clean_value[: max_length - 1].rstrip()}..."
