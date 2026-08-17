from __future__ import annotations

from typing import Sequence

import numpy as np

from services.preferred_work_grouping_service import PreferredWorkGrouper, WORK_FIELDS


class MeaningEmbeddingModel:
    model_name = "test/meaning-embedding"

    def __init__(self) -> None:
        self.query_batches = 0

    def encode(self, texts: Sequence[str], *, kind: str) -> np.ndarray:
        vectors = []
        for text in texts:
            dimensions = len(WORK_FIELDS) + 3
            if kind == "document":
                field_index = next(
                    index
                    for index, field in enumerate(WORK_FIELDS)
                    if text in field.anchors
                )
                vector = np.zeros(dimensions, dtype=np.float32)
                vector[field_index] = 1.0
            else:
                self.query_batches += 1
                clean = text.casefold()
                vector = np.zeros(dimensions, dtype=np.float32)
                if "software" in clean:
                    vector[1] = 1.0
                elif "office" in clean or "forms" in clean:
                    vector[2] = 1.0
                elif "animal" in clean or "pet" in clean:
                    vector[len(WORK_FIELDS)] = 1.0
                elif "garden" in clean or "compost" in clean:
                    vector[len(WORK_FIELDS) + 1] = 1.0
                else:
                    vector[len(WORK_FIELDS) + 2] = 1.0
            vectors.append(vector)
        return np.asarray(vectors, dtype=np.float32)


def test_embedding_grouper_assigns_stable_fields_and_reviews_ambiguous_text() -> None:
    model = MeaningEmbeddingModel()
    grouper = PreferredWorkGrouper(model)

    grouping = grouper.group(
        ["Software development", "office work with forms", "anything available"]
    )

    assert grouping.model_available is True
    assert grouping.for_value("software-development").field_label == "Data & Technology"
    assert grouping.for_value("Office work with forms").field_label == "Business & Administration"
    assert grouping.for_value("anything available").field_label == "Flexible / Open to Any Role"
    assert grouping.for_value("anything available").needs_review is False


def test_embedding_grouper_caches_normalized_answers() -> None:
    model = MeaningEmbeddingModel()
    grouper = PreferredWorkGrouper(model)

    grouper.group(["Software development"])
    first_query_count = model.query_batches
    grouper.group([" software-development "])

    assert model.query_batches == first_query_count


def test_embedding_grouper_discovers_repeated_novel_themes_but_not_singletons() -> None:
    grouper = PreferredWorkGrouper(MeaningEmbeddingModel())

    grouping = grouper.group(
        [
            "helping w animals at a shelter",
            "pet and animal care",
            "urban garden and compost work",
            "anything available",
            "anything available",
            "anything available",
        ]
    )

    animal_one = grouping.for_value("helping w animals at a shelter")
    animal_two = grouping.for_value("pet and animal care")
    assert animal_one is not None and animal_two is not None
    assert animal_one.field_code == animal_two.field_code
    assert animal_one.is_emerging is True
    assert animal_one.method == "semantic_discovery"
    assert grouping.for_value("urban garden and compost work").field_label == "Needs Review"
    assert grouping.for_value("anything available").field_label == "Flexible / Open to Any Role"
    assert grouping.for_value("anything available").is_emerging is False


class BrokenEmbeddingModel:
    model_name = "test/broken"

    def encode(self, texts: Sequence[str], *, kind: str) -> np.ndarray:
        raise RuntimeError("model unavailable")


def test_embedding_failure_sends_answers_to_review() -> None:
    grouping = PreferredWorkGrouper(BrokenEmbeddingModel()).group(["Data analysis"])

    assignment = grouping.for_value("Data analysis")
    assert grouping.model_available is False
    assert assignment is not None
    assert assignment.field_label == "Needs Review"
    assert assignment.method == "embedding_unavailable"


def test_explicit_flexibility_is_recognized_without_the_embedding_model() -> None:
    grouping = PreferredWorkGrouper(BrokenEmbeddingModel()).group(
        ["open to any role wherever needed", "any position is fine im flexible", "not sure what i want"]
    )

    for value in ("open to any role wherever needed", "any position is fine im flexible"):
        assignment = grouping.for_value(value)
        assert assignment is not None
        assert assignment.field_label == "Flexible / Open to Any Role"
        assert assignment.method == "explicit_flexible"
        assert assignment.needs_review is False

    uncertain = grouping.for_value("not sure what i want")
    assert uncertain is not None
    assert uncertain.field_label == "Needs Review"
    assert uncertain.needs_review is True
