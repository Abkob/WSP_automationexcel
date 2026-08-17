from __future__ import annotations

from typing import Sequence

import numpy as np

from services.technical_skill_grouping_service import SKILL_TOPICS, TechnicalSkillGrouper


class SkillMeaningEmbeddingModel:
    model_name = "test/skill-meaning"

    def encode(self, texts: Sequence[str], *, kind: str) -> np.ndarray:
        vectors = []
        for text in texts:
            vector = np.zeros(len(SKILL_TOPICS) + 2, dtype=np.float32)
            clean = text.casefold()
            if kind == "document":
                topic_index = next(
                    index for index, topic in enumerate(SKILL_TOPICS) if text in topic.anchors
                )
                vector[topic_index] = 1.0
            elif "python" in clean or "pyhton" in clean:
                vector[0] = 1.0
            elif "drone" in clean or "uav" in clean:
                vector[len(SKILL_TOPICS)] = 1.0
            else:
                vector[len(SKILL_TOPICS) + 1] = 1.0
            vectors.append(vector)
        return np.asarray(vectors, dtype=np.float32)


def test_skills_are_split_and_grouped_semantically_between_students() -> None:
    grouping = TechnicalSkillGrouper(SkillMeaningEmbeddingModel()).group(
        [
            "pyhton scripting, drone piloting",
            "Python automation and UAV flight controls",
            "banana juggling",
        ]
    )

    assert grouping.for_term("pyhton scripting").topic_label == "Python"
    assert grouping.for_term("Python automation").topic_label == "Python"

    drone = grouping.for_term("drone piloting")
    uav = grouping.for_term("UAV flight controls")
    assert drone is not None and uav is not None
    assert drone.topic_code == uav.topic_code
    assert drone.topic_label.startswith("Emerging ·")
    assert drone.is_emerging is True

    singleton = grouping.for_term("banana juggling")
    assert singleton is not None
    assert singleton.topic_label == "Unverified / Needs Review"
    assert singleton.needs_review is True


def test_same_unfamiliar_skill_repeated_by_two_students_creates_a_topic() -> None:
    grouping = TechnicalSkillGrouper(SkillMeaningEmbeddingModel()).group(
        ["banana juggling", "banana juggling"]
    )

    assignment = grouping.for_term("banana juggling")
    assert assignment is not None
    assert assignment.is_emerging is True
    assert assignment.needs_review is False


def test_one_student_cannot_create_a_dynamic_topic_by_repeating_it() -> None:
    grouping = TechnicalSkillGrouper(SkillMeaningEmbeddingModel()).group(
        ["drone piloting, drone piloting"]
    )

    assignment = grouping.for_term("drone piloting")
    assert assignment is not None
    assert assignment.topic_label == "Unverified / Needs Review"
    assert assignment.needs_review is True


def test_known_aliases_are_stable_without_semantic_discovery() -> None:
    grouping = TechnicalSkillGrouper(SkillMeaningEmbeddingModel()).group(
        ["MS Excel, SQL Server, Canva"]
    )

    assert grouping.for_term("MS Excel").topic_label == "Excel & Spreadsheets"
    assert grouping.for_term("SQL Server").topic_label == "SQL & Databases"
    assert grouping.for_term("Canva").topic_label == "Graphic Design & Canva"
    assert all(not assignment.is_emerging for assignment in grouping.assignments.values())


def test_repeated_import_markers_never_become_skill_topics() -> None:
    grouping = TechnicalSkillGrouper(SkillMeaningEmbeddingModel()).group(
        ["Updated W5", "Updated W5", "Updated W6"]
    )

    for value in ("Updated W5", "Updated W6"):
        assignment = grouping.for_term(value)
        assert assignment is not None
        assert assignment.topic_label == "Unverified / Needs Review"
        assert assignment.method == "non_skill_marker"
        assert assignment.is_emerging is False
