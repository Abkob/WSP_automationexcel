from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha1
from threading import RLock
from typing import Iterable

import numpy as np

from config import AppSettings
from services.analytics_service import normalize_subjective_term
from services.embedding_service import EmbeddingModel, get_default_embedding_model


@dataclass(frozen=True)
class WorkField:
    code: str
    label: str
    color: str
    anchors: tuple[str, ...]


WORK_FIELDS: tuple[WorkField, ...] = (
    WorkField(
        "research",
        "Research & Analysis",
        "#840132",
        (
            "research assistance",
            "policy research",
            "academic research and literature reviews",
            "survey design, interviews and qualitative analysis",
            "collecting and analyzing information for a research project",
        ),
    ),
    WorkField(
        "data_technology",
        "Data & Technology",
        "#1F5A7A",
        (
            "software development and programming",
            "data analysis and spreadsheet reporting",
            "database, website and information technology support",
            "automation, coding and technical computing",
            "digital systems and data entry quality checks",
        ),
    ),
    WorkField(
        "business_admin",
        "Business & Administration",
        "#6D4C41",
        (
            "office administration and clerical work",
            "operations management and project coordination",
            "human resources and customer service",
            "organizing events, records, forms and schedules",
            "general business and administrative support",
        ),
    ),
    WorkField(
        "finance_accounting",
        "Finance & Accounting",
        "#B86B1F",
        (
            "accounting and audit support",
            "budgeting, bookkeeping and invoice tracking",
            "financial analysis and finance support",
            "working with financial records and reports",
        ),
    ),
    WorkField(
        "design_media",
        "Design, Media & Communications",
        "#A63D73",
        (
            "graphic design and visual content creation",
            "digital marketing and social media",
            "writing, editing and communications",
            "creative media, photography and video",
            "content editing and publication support",
        ),
    ),
    WorkField(
        "engineering_architecture",
        "Engineering & Architecture",
        "#5B4B8A",
        (
            "engineering and electronics work",
            "hardware design and technical systems",
            "architectural drawing, CAD and drafting",
            "construction, prototyping and technical design",
        ),
    ),
    WorkField(
        "health_community",
        "Health & Community Services",
        "#0F766E",
        (
            "clinical support and patient care",
            "nursing and healthcare assistance",
            "public health and health promotion",
            "community outreach and wellbeing programs",
        ),
    ),
    WorkField(
        "laboratory_quality",
        "Laboratory & Quality",
        "#4F7A4A",
        (
            "laboratory assistance and experiments",
            "sample preparation and scientific testing",
            "quality assurance and quality control",
            "lab records, equipment and safety support",
        ),
    ),
    WorkField(
        "education_support",
        "Education & Student Support",
        "#4B5AA7",
        (
            "tutoring and teaching assistance",
            "mentoring and helping students",
            "student services and academic support",
            "library, orientation and campus program assistance",
        ),
    ),
)

REVIEW_FIELD = WorkField("review", "Needs Review", "#64748B", ())
FLEXIBLE_FIELD = WorkField("flexible", "Flexible / Open to Any Role", "#0E7490", ())
EMERGING_COLORS = ("#7C3AED", "#0E7490", "#C2410C", "#3F6212", "#9F1239", "#4338CA")
FLEXIBLE_PREFERENCES = {
    "anything",
    "anything available",
    "anything lol need hrs",
    "any work",
    "whatever",
    "no preference",
    "open to anything",
    "open to any role",
    "open to any work",
    "any role",
    "any position",
    "wherever needed",
    "flexible",
}
UNCERTAIN_PREFERENCES = {
    "not sure",
    "idk",
    "i dont know",
    "i don't know",
    "need hours",
}


@dataclass(frozen=True)
class PreferredWorkAssignment:
    field_code: str
    field_label: str
    color: str
    confidence: float | None
    margin: float | None
    needs_review: bool
    method: str
    is_emerging: bool = False


@dataclass(frozen=True)
class PreferredWorkGrouping:
    assignments: dict[str, PreferredWorkAssignment]
    model_name: str
    model_available: bool

    def for_value(self, value: object) -> PreferredWorkAssignment | None:
        key = normalized_preference_key(value)
        return self.assignments.get(key) if key else None


class PreferredWorkGrouper:
    """Groups free-text work preferences without changing their original text."""

    def __init__(
        self,
        embedding_model: EmbeddingModel,
        *,
        minimum_similarity: float = 0.60,
        minimum_margin: float = 0.035,
        discovery_similarity: float = 0.68,
        discovery_candidate_ceiling: float = 0.70,
        minimum_cluster_responses: int = 2,
    ) -> None:
        self.embedding_model = embedding_model
        self.minimum_similarity = minimum_similarity
        self.minimum_margin = minimum_margin
        self.discovery_similarity = discovery_similarity
        self.discovery_candidate_ceiling = discovery_candidate_ceiling
        self.minimum_cluster_responses = minimum_cluster_responses
        self._anchor_vectors: np.ndarray | None = None
        self._field_slices: tuple[slice, ...] = ()
        self._cache: dict[str, PreferredWorkAssignment] = {}
        self._vector_cache: dict[str, np.ndarray] = {}
        self._lock = RLock()

    def group(self, values: Iterable[object]) -> PreferredWorkGrouping:
        value_list = list(values)
        normalized: dict[str, str] = {}
        response_counts: dict[str, int] = {}
        for value in value_list:
            key = normalized_preference_key(value)
            if not key:
                continue
            normalized[key] = normalize_subjective_term(value)
            response_counts[key] = response_counts.get(key, 0) + 1
        missing = {key: text for key, text in normalized.items() if key not in self._cache}
        model_available = True
        if missing:
            with self._lock:
                missing = {key: text for key, text in missing.items() if key not in self._cache}
                if missing:
                    flexible_keys = {key for key in missing if is_flexible_preference(key)}
                    for key in flexible_keys:
                        self._cache[key] = flexible_assignment()
                    missing = {key: text for key, text in missing.items() if key not in flexible_keys}
                if missing:
                    try:
                        self._ensure_anchor_vectors()
                        query_vectors = self.embedding_model.encode(list(missing.values()), kind="query")
                        for (key, _text), vector in zip(missing.items(), query_vectors, strict=True):
                            self._vector_cache[key] = np.asarray(vector, dtype=np.float32)
                            self._cache[key] = review_assignment(method="uncertain_response") if is_uncertain_preference(key) else self._classify(vector)
                    except Exception:
                        model_available = False
                        for key in missing:
                            self._cache[key] = review_assignment(method="embedding_unavailable")

        selected = {key: self._cache[key] for key in normalized}
        if model_available:
            selected.update(self._discover_emerging_fields(selected, normalized, response_counts))
        if any(item.method == "embedding_unavailable" for item in selected.values()):
            model_available = False
        return PreferredWorkGrouping(
            assignments=selected,
            model_name=self.embedding_model.model_name,
            model_available=model_available,
        )

    def _discover_emerging_fields(
        self,
        selected: dict[str, PreferredWorkAssignment],
        normalized: dict[str, str],
        response_counts: dict[str, int],
    ) -> dict[str, PreferredWorkAssignment]:
        candidates = [
            key
            for key, assignment in selected.items()
            if assignment.method == "offline_embedding"
            and (
                assignment.needs_review
                or (
                    assignment.confidence is not None
                    and assignment.confidence < self.discovery_candidate_ceiling
                )
            )
            and key in self._vector_cache
            and not is_uncertain_preference(key)
        ]
        if not candidates:
            return {}

        vectors = np.asarray([self._vector_cache[key] for key in candidates], dtype=np.float32)
        similarity = vectors @ vectors.T
        clusters: list[list[int]] = [[index] for index in range(len(candidates))]

        while True:
            best_pair: tuple[int, int] | None = None
            best_score = -1.0
            for left in range(len(clusters)):
                for right in range(left + 1, len(clusters)):
                    cross_scores = similarity[np.ix_(clusters[left], clusters[right])]
                    complete_link_score = float(np.min(cross_scores))
                    if complete_link_score >= self.discovery_similarity and complete_link_score > best_score:
                        best_pair = (left, right)
                        best_score = complete_link_score
            if best_pair is None:
                break
            left, right = best_pair
            clusters[left] = clusters[left] + clusters[right]
            clusters.pop(right)

        emerging: dict[str, PreferredWorkAssignment] = {}
        for cluster in clusters:
            keys = [candidates[index] for index in cluster]
            response_total = sum(response_counts[key] for key in keys)
            enough_evidence = len(keys) >= 2 or response_total >= max(3, self.minimum_cluster_responses)
            if not enough_evidence or response_total < self.minimum_cluster_responses:
                continue

            cluster_scores = similarity[np.ix_(cluster, cluster)]
            mean_scores = np.mean(cluster_scores, axis=1)
            central_order = sorted(
                range(len(keys)),
                key=lambda index: (-float(mean_scores[index]), -response_counts[keys[index]], keys[index]),
            )
            representative_key = keys[central_order[0]]
            representative = normalized[representative_key]
            label_text = representative if len(representative) <= 42 else f"{representative[:39].rstrip()}…"
            digest = sha1(representative_key.encode("utf-8")).hexdigest()
            color = EMERGING_COLORS[int(digest[:8], 16) % len(EMERGING_COLORS)]
            field_code = f"emerging_{digest[:10]}"
            cohesion = float(np.mean(cluster_scores))
            for key in keys:
                emerging[key] = PreferredWorkAssignment(
                    field_code=field_code,
                    field_label=f"Emerging · {label_text}",
                    color=color,
                    confidence=round(cohesion, 3),
                    margin=None,
                    needs_review=False,
                    method="semantic_discovery",
                    is_emerging=True,
                )
        return emerging

    def _ensure_anchor_vectors(self) -> None:
        if self._anchor_vectors is not None:
            return
        anchors: list[str] = []
        slices: list[slice] = []
        for field in WORK_FIELDS:
            start = len(anchors)
            anchors.extend(field.anchors)
            slices.append(slice(start, len(anchors)))
        self._anchor_vectors = self.embedding_model.encode(anchors, kind="document")
        self._field_slices = tuple(slices)

    def _classify(self, query_vector: np.ndarray) -> PreferredWorkAssignment:
        assert self._anchor_vectors is not None
        similarities = np.asarray(query_vector, dtype=np.float32) @ self._anchor_vectors.T
        field_scores = np.asarray(
            [float(np.max(similarities[field_slice])) for field_slice in self._field_slices],
            dtype=np.float32,
        )
        order = np.argsort(field_scores)[::-1]
        best_index = int(order[0])
        best_score = float(field_scores[best_index])
        second_score = float(field_scores[int(order[1])]) if len(order) > 1 else 0.0
        margin = best_score - second_score
        if best_score < self.minimum_similarity or margin < self.minimum_margin:
            return PreferredWorkAssignment(
                field_code=REVIEW_FIELD.code,
                field_label=REVIEW_FIELD.label,
                color=REVIEW_FIELD.color,
                confidence=round(best_score, 3),
                margin=round(margin, 3),
                needs_review=True,
                method="offline_embedding",
            )
        field = WORK_FIELDS[best_index]
        return PreferredWorkAssignment(
            field_code=field.code,
            field_label=field.label,
            color=field.color,
            confidence=round(best_score, 3),
            margin=round(margin, 3),
            needs_review=False,
            method="offline_embedding",
        )


def normalized_preference_key(value: object) -> str:
    return normalize_subjective_term(value).casefold()


def is_flexible_preference(key: str) -> bool:
    clean = key.strip().casefold()
    return clean in FLEXIBLE_PREFERENCES or clean.startswith(
        (
            "anything ",
            "any work ",
            "any role ",
            "any position ",
            "whatever ",
            "open to any",
            "wherever needed",
        )
    )


def is_uncertain_preference(key: str) -> bool:
    clean = key.strip().casefold()
    return clean in UNCERTAIN_PREFERENCES or clean.startswith(("idk ", "not sure ", "i dont know ", "i don't know "))


def flexible_assignment() -> PreferredWorkAssignment:
    return PreferredWorkAssignment(
        field_code=FLEXIBLE_FIELD.code,
        field_label=FLEXIBLE_FIELD.label,
        color=FLEXIBLE_FIELD.color,
        confidence=1.0,
        margin=None,
        needs_review=False,
        method="explicit_flexible",
    )


def review_assignment(*, method: str = "not_grouped") -> PreferredWorkAssignment:
    return PreferredWorkAssignment(
        field_code=REVIEW_FIELD.code,
        field_label=REVIEW_FIELD.label,
        color=REVIEW_FIELD.color,
        confidence=None,
        margin=None,
        needs_review=True,
        method=method,
    )


def ungrouped_preferences(values: Iterable[object]) -> PreferredWorkGrouping:
    assignments = {
        key: review_assignment()
        for value in values
        if (key := normalized_preference_key(value))
    }
    return PreferredWorkGrouping(assignments=assignments, model_name="unavailable", model_available=False)


@lru_cache(maxsize=4)
def get_default_preferred_work_grouper(settings: AppSettings) -> PreferredWorkGrouper:
    return PreferredWorkGrouper(get_default_embedding_model(settings))
