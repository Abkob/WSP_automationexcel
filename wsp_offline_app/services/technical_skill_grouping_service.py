from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha1
import re
from threading import RLock
from typing import Iterable

import numpy as np

from config import AppSettings
from services.analytics_service import normalize_subjective_term, split_subjective_terms
from services.embedding_service import EmbeddingModel, get_default_embedding_model


@dataclass(frozen=True)
class SkillTopic:
    code: str
    label: str
    color: str
    anchors: tuple[str, ...]
    exact_terms: tuple[str, ...] = ()


SKILL_TOPICS: tuple[SkillTopic, ...] = (
    SkillTopic("python", "Python", "#3776AB", ("Python programming", "Python scripting and automation"), ("python", "py")),
    SkillTopic("excel", "Excel & Spreadsheets", "#217346", ("Microsoft Excel", "spreadsheet formulas and reporting", "pivot tables in Excel"), ("excel", "spreadsheets", "ms excel", "microsoft excel")),
    SkillTopic("sql_databases", "SQL & Databases", "#336791", ("SQL database queries", "relational database management", "database design and administration"), ("sql", "sql server")),
    SkillTopic("data_analysis", "Data Analysis & Visualization", "#1F5A7A", ("data analysis and visualization", "statistical analysis and dashboards", "data cleaning and reporting"), ("spss", "nvivo", "gis", "arcgis", "matlab")),
    SkillTopic("software", "Software Development", "#5B4B8A", ("software development and programming", "application development and debugging", "coding and source control"), ("git", "c", "c++", "vhdl")),
    SkillTopic("web", "Web Development", "#7C3AED", ("HTML CSS and JavaScript web development", "frontend website development", "backend web application development"), ("html", "css", "javascript")),
    SkillTopic("office", "Microsoft Office", "#B86B1F", ("Microsoft Office applications", "Word PowerPoint and Outlook", "office productivity software"), ("microsoft office", "ms office", "powerpoint", "microsoft word")),
    SkillTopic("design", "Graphic Design & Canva", "#A63D73", ("graphic design and Canva", "Adobe Photoshop and Illustrator", "visual layouts and poster design"), ("canva", "photoshop", "adobe photoshop", "illustrator", "adobe illustrator", "figma")),
    SkillTopic("cad", "CAD & Technical Drawing", "#C2410C", ("AutoCAD technical drawing", "computer aided design and drafting", "architectural CAD modeling"), ("autocad", "cad", "revit", "sketchup")),
    SkillTopic("media", "Photography & Video", "#9F1239", ("photography and video production", "video editing and filming", "digital media production"), ("photography", "video editing")),
    SkillTopic("laboratory", "Laboratory Techniques", "#4F7A4A", ("laboratory techniques and equipment", "sample preparation and lab safety", "scientific testing in a laboratory"), ("nmr", "hplc", "titration", "pcr", "elisa", "microscopy")),
    SkillTopic("clinical", "Clinical & Health Systems", "#0F766E", ("clinical assessment and health systems", "electronic medical records and patient documentation", "epidemiology and public health analysis"), ("patient assessment", "emr", "epidemiology")),
    SkillTopic("accounting", "Accounting & Finance Tools", "#8A6116", ("accounting and bookkeeping software", "financial records and invoice tracking", "budget spreadsheets and bookkeeping"), ("sap", "quickbooks", "ifrs", "bloomberg")),
    SkillTopic("research", "Research & Academic Methods", "#840132", ("academic research methods", "survey interviews and literature reviews", "qualitative and quantitative research"), ("policy analysis", "academic writing", "editing")),
    SkillTopic("marketing", "Digital Marketing & Social Media", "#D04A68", ("digital marketing and social media management", "content scheduling and online campaigns", "social media analytics"), ("google analytics", "seo")),
    SkillTopic("it_support", "IT Support & Networking", "#0E7490", ("computer troubleshooting and IT support", "network administration and hardware support", "technical help desk support")),
)

REVIEW_TOPIC = SkillTopic("review", "Unverified / Needs Review", "#64748B", ())
EMERGING_COLORS = ("#7C3AED", "#0E7490", "#C2410C", "#3F6212", "#9F1239", "#4338CA")
UNCERTAIN_SKILLS = {"none", "n/a", "na", "not sure", "idk", "no skills", "nothing", "unknown"}
NON_SKILL_MARKER_RE = re.compile(r"^(?:updated?|test(?:ing)?|sample|placeholder)\s*(?:w(?:eek)?\s*)?\d*$", re.IGNORECASE)


@dataclass(frozen=True)
class TechnicalSkillAssignment:
    topic_code: str
    topic_label: str
    color: str
    confidence: float | None
    needs_review: bool
    method: str
    is_emerging: bool = False


@dataclass(frozen=True)
class TechnicalSkillGrouping:
    assignments: dict[str, TechnicalSkillAssignment]
    model_name: str
    model_available: bool

    def for_term(self, value: object) -> TechnicalSkillAssignment | None:
        key = normalized_skill_key(value)
        return self.assignments.get(key) if key else None

    def assignments_for_value(self, value: object) -> tuple[TechnicalSkillAssignment, ...]:
        assignments: list[TechnicalSkillAssignment] = []
        seen: set[str] = set()
        for term in split_subjective_terms(value, split_on_and=True):
            assignment = self.for_term(term)
            if assignment and assignment.topic_code not in seen:
                assignments.append(assignment)
                seen.add(assignment.topic_code)
        return tuple(assignments)


class TechnicalSkillGrouper:
    """Builds technical-skill topics from rough text across the student population."""

    def __init__(
        self,
        embedding_model: EmbeddingModel,
        *,
        minimum_similarity: float = 0.62,
        minimum_margin: float = 0.025,
        discovery_similarity: float = 0.72,
        discovery_candidate_ceiling: float = 0.72,
        minimum_cluster_students: int = 2,
    ) -> None:
        self.embedding_model = embedding_model
        self.minimum_similarity = minimum_similarity
        self.minimum_margin = minimum_margin
        self.discovery_similarity = discovery_similarity
        self.discovery_candidate_ceiling = discovery_candidate_ceiling
        self.minimum_cluster_students = minimum_cluster_students
        self._anchor_vectors: np.ndarray | None = None
        self._topic_slices: tuple[slice, ...] = ()
        self._cache: dict[str, TechnicalSkillAssignment] = {}
        self._vector_cache: dict[str, np.ndarray] = {}
        self._lock = RLock()
        self._exact_topics = {
            normalized_skill_key(term): topic
            for topic in SKILL_TOPICS
            for term in (topic.label, *topic.exact_terms)
        }

    def group(self, values: Iterable[object]) -> TechnicalSkillGrouping:
        value_list = list(values)
        normalized: dict[str, str] = {}
        students_by_term: dict[str, set[int]] = defaultdict(set)
        for student_index, value in enumerate(value_list):
            for raw_term in split_subjective_terms(value, split_on_and=True):
                key = normalized_skill_key(raw_term)
                if not key:
                    continue
                normalized[key] = normalize_subjective_term(raw_term)
                students_by_term[key].add(student_index)

        missing = {key: text for key, text in normalized.items() if key not in self._cache}
        model_available = True
        if missing:
            with self._lock:
                missing = {key: text for key, text in missing.items() if key not in self._cache}
                for key in tuple(missing):
                    if topic := self._exact_topics.get(key):
                        self._cache[key] = topic_assignment(topic, method="known_skill")
                        missing.pop(key)
                    elif is_uncertain_skill(key) or is_non_skill_marker(key):
                        method = "non_skill_marker" if is_non_skill_marker(key) else "uncertain_response"
                        self._cache[key] = review_assignment(method=method)
                        missing.pop(key)
                if missing:
                    try:
                        self._ensure_anchor_vectors()
                        query_vectors = self.embedding_model.encode(list(missing.values()), kind="query")
                        for (key, _text), vector in zip(missing.items(), query_vectors, strict=True):
                            self._vector_cache[key] = np.asarray(vector, dtype=np.float32)
                            self._cache[key] = self._classify(vector)
                    except Exception:
                        model_available = False
                        for key in missing:
                            self._cache[key] = review_assignment(method="embedding_unavailable")

        selected = {key: self._cache[key] for key in normalized}
        if model_available:
            selected.update(self._discover_topics(selected, normalized, students_by_term))
        if any(item.method == "embedding_unavailable" for item in selected.values()):
            model_available = False
        return TechnicalSkillGrouping(selected, self.embedding_model.model_name, model_available)

    def _discover_topics(
        self,
        selected: dict[str, TechnicalSkillAssignment],
        normalized: dict[str, str],
        students_by_term: dict[str, set[int]],
    ) -> dict[str, TechnicalSkillAssignment]:
        candidates = [
            key
            for key, assignment in selected.items()
            if assignment.method == "offline_embedding"
            and (
                assignment.needs_review
                or (assignment.confidence is not None and assignment.confidence < self.discovery_candidate_ceiling)
            )
            and key in self._vector_cache
            and not is_uncertain_skill(key)
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
                    score = float(np.min(similarity[np.ix_(clusters[left], clusters[right])]))
                    if score >= self.discovery_similarity and score > best_score:
                        best_pair = (left, right)
                        best_score = score
            if best_pair is None:
                break
            left, right = best_pair
            clusters[left] += clusters[right]
            clusters.pop(right)

        emerging: dict[str, TechnicalSkillAssignment] = {}
        for cluster in clusters:
            keys = [candidates[index] for index in cluster]
            evidence_students = set().union(*(students_by_term[key] for key in keys))
            if len(evidence_students) < self.minimum_cluster_students:
                continue
            cluster_scores = similarity[np.ix_(cluster, cluster)]
            mean_scores = np.mean(cluster_scores, axis=1)
            representative_index = max(
                range(len(keys)),
                key=lambda index: (float(mean_scores[index]), len(students_by_term[keys[index]]), -len(normalized[keys[index]])),
            )
            representative = normalized[keys[representative_index]]
            label_text = representative if len(representative) <= 38 else f"{representative[:35].rstrip()}…"
            digest = sha1("|".join(sorted(keys)).encode("utf-8")).hexdigest()
            color = EMERGING_COLORS[int(digest[:8], 16) % len(EMERGING_COLORS)]
            cohesion = float(np.mean(cluster_scores))
            for key in keys:
                emerging[key] = TechnicalSkillAssignment(
                    topic_code=f"emerging_{digest[:10]}",
                    topic_label=f"Emerging · {label_text}",
                    color=color,
                    confidence=round(cohesion, 3),
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
        for topic in SKILL_TOPICS:
            start = len(anchors)
            anchors.extend(topic.anchors)
            slices.append(slice(start, len(anchors)))
        self._anchor_vectors = self.embedding_model.encode(anchors, kind="document")
        self._topic_slices = tuple(slices)

    def _classify(self, query_vector: np.ndarray) -> TechnicalSkillAssignment:
        assert self._anchor_vectors is not None
        similarities = np.asarray(query_vector, dtype=np.float32) @ self._anchor_vectors.T
        topic_scores = np.asarray(
            [float(np.max(similarities[topic_slice])) for topic_slice in self._topic_slices],
            dtype=np.float32,
        )
        order = np.argsort(topic_scores)[::-1]
        best_index = int(order[0])
        best_score = float(topic_scores[best_index])
        second_score = float(topic_scores[int(order[1])]) if len(order) > 1 else 0.0
        if best_score < self.minimum_similarity or best_score - second_score < self.minimum_margin:
            return review_assignment(method="offline_embedding", confidence=best_score)
        return topic_assignment(SKILL_TOPICS[best_index], method="offline_embedding", confidence=best_score)


def normalized_skill_key(value: object) -> str:
    return normalize_subjective_term(value).casefold()


def is_uncertain_skill(key: str) -> bool:
    clean = key.strip().casefold()
    return clean in UNCERTAIN_SKILLS or clean.startswith(("idk ", "not sure ", "no skill"))


def is_non_skill_marker(key: str) -> bool:
    return bool(NON_SKILL_MARKER_RE.fullmatch(key.strip()))


def topic_assignment(
    topic: SkillTopic,
    *,
    method: str,
    confidence: float | None = 1.0,
) -> TechnicalSkillAssignment:
    return TechnicalSkillAssignment(
        topic.code,
        topic.label,
        topic.color,
        round(confidence, 3) if confidence is not None else None,
        False,
        method,
    )


def review_assignment(*, method: str, confidence: float | None = None) -> TechnicalSkillAssignment:
    return TechnicalSkillAssignment(
        REVIEW_TOPIC.code,
        REVIEW_TOPIC.label,
        REVIEW_TOPIC.color,
        round(confidence, 3) if confidence is not None else None,
        True,
        method,
    )


def ungrouped_technical_skills(values: Iterable[object]) -> TechnicalSkillGrouping:
    assignments: dict[str, TechnicalSkillAssignment] = {}
    for value in values:
        for term in split_subjective_terms(value, split_on_and=True):
            key = normalized_skill_key(term)
            if key:
                label = normalize_subjective_term(term)
                assignments[key] = TechnicalSkillAssignment(key, label, "#1F5A7A", None, False, "literal")
    return TechnicalSkillGrouping(assignments, "unavailable", False)


@lru_cache(maxsize=4)
def get_default_technical_skill_grouper(settings: AppSettings) -> TechnicalSkillGrouper:
    return TechnicalSkillGrouper(get_default_embedding_model(settings))
