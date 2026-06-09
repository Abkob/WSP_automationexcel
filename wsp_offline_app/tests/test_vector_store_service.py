from __future__ import annotations

import numpy as np

from services.vector_store_service import FaissVectorStore, VectorRecord


def test_faiss_vector_store_upserts_and_queries_by_similarity(tmp_path) -> None:
    store = FaissVectorStore(tmp_path, collection_name="students")
    store.upsert(
        (
            VectorRecord("1001", np.array([1.0, 0.0], dtype=np.float32), {"semantic_hash": "a"}, "admin profile"),
            VectorRecord("1002", np.array([0.0, 1.0], dtype=np.float32), {"semantic_hash": "b"}, "lab profile"),
        )
    )

    results = store.query(np.array([0.9, 0.1], dtype=np.float32), top_k=2)

    assert store.count() == 2
    assert [result.record_id for result in results] == ["1001", "1002"]
    assert results[0].metadata["semantic_hash"] == "a"
    assert store.index_path.exists()
    assert store.vectors_path.exists()
    assert store.metadata_path.exists()


def test_vector_store_query_respects_candidate_ids_and_minimum_score(tmp_path) -> None:
    store = FaissVectorStore(tmp_path, collection_name="students")
    store.replace_all(
        (
            VectorRecord("1001", np.array([1.0, 0.0], dtype=np.float32), {}, "admin profile"),
            VectorRecord("1002", np.array([0.0, 1.0], dtype=np.float32), {}, "lab profile"),
        )
    )

    results = store.query(
        np.array([1.0, 0.0], dtype=np.float32),
        top_k=5,
        candidate_ids={"1002"},
        minimum_score=0.0,
    )

    assert [result.record_id for result in results] == ["1002"]
    assert results[0].score == 0.0


def test_vector_store_upsert_replaces_existing_record(tmp_path) -> None:
    store = FaissVectorStore(tmp_path, collection_name="students")
    store.upsert((VectorRecord("1001", np.array([1.0, 0.0], dtype=np.float32), {"version": 1}, "old"),))
    store.upsert((VectorRecord("1001", np.array([0.0, 1.0], dtype=np.float32), {"version": 2}, "new"),))

    results = store.query(np.array([0.0, 1.0], dtype=np.float32), top_k=1)

    assert results[0].record_id == "1001"
    assert results[0].metadata["version"] == 2
    assert results[0].document == "new"
