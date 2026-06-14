from __future__ import annotations

import json
import re
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from services.embedding_service import normalize_embedding_matrix


DEFAULT_VECTOR_STORE_NAME = "faiss"

# ── in-process cache for the loaded vector matrix + metadata ─────────────────
# Keyed by the absolute path of the vectors file.
# Entry: (matrix, metadata_list, vectors_mtime, metadata_mtime)
# Invalidated automatically when either file's mtime changes (i.e. after upsert).
_VECTOR_CACHE: dict[Path, tuple[np.ndarray, list[dict], float, float]] = {}
_VECTOR_CACHE_LOCK = threading.Lock()


@dataclass(frozen=True)
class VectorRecord:
    record_id: str
    embedding: np.ndarray
    metadata: dict[str, Any]
    document: str


@dataclass(frozen=True)
class VectorSearchResult:
    record_id: str
    score: float
    metadata: dict[str, Any]
    document: str


class FaissVectorStore:
    def __init__(self, index_dir: Path | str, *, collection_name: str = "students") -> None:
        self.index_dir = Path(index_dir).resolve()
        self.collection_name = safe_collection_name(collection_name)

    @property
    def index_path(self) -> Path:
        return self.index_dir / f"{self.collection_name}.faiss"

    @property
    def metadata_path(self) -> Path:
        return self.index_dir / f"{self.collection_name}_metadata.json"

    @property
    def vectors_path(self) -> Path:
        return self.index_dir / f"{self.collection_name}_vectors.npy"

    @property
    def vector_store_name(self) -> str:
        return DEFAULT_VECTOR_STORE_NAME

    def replace_all(self, records: Iterable[VectorRecord]) -> None:
        ordered_records = tuple(records)
        self.index_dir.mkdir(parents=True, exist_ok=True)

        if not ordered_records:
            self._invalidate_cache()
            self.metadata_path.write_text("[]", encoding="utf-8")
            np.save(self.vectors_path, np.empty((0, 0), dtype=np.float32))
            if self.index_path.exists():
                self.index_path.unlink()
            return

        self._invalidate_cache()
        matrix = normalize_embedding_matrix(np.vstack([np.asarray(record.embedding, dtype=np.float32) for record in ordered_records]))
        write_faiss_index(self.index_path, matrix)
        np.save(self.vectors_path, matrix)
        self.metadata_path.write_text(
            json.dumps(
                [
                    {
                        "record_id": record.record_id,
                        "metadata": record.metadata,
                        "document": record.document,
                    }
                    for record in ordered_records
                ],
                ensure_ascii=True,
                sort_keys=True,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )

    def upsert(self, records: Iterable[VectorRecord]) -> None:
        incoming = tuple(records)
        if not incoming:
            return
        existing_records = self.load_records()
        by_id = {record.record_id: record for record in existing_records}
        for record in incoming:
            by_id[record.record_id] = record
        self.replace_all(by_id.values())

    def query(
        self,
        query_embedding: np.ndarray,
        *,
        top_k: int,
        candidate_ids: Iterable[str] | None = None,
        minimum_score: float | None = None,
    ) -> tuple[VectorSearchResult, ...]:
        if top_k <= 0:
            raise ValueError("top_k must be positive")
        matrix, metadata_rows = self._load_cached()
        if matrix.size == 0 or not metadata_rows:
            return ()

        query_vector = normalize_embedding_matrix(np.asarray(query_embedding, dtype=np.float32))[0]
        candidate_id_set = set(candidate_ids) if candidate_ids is not None else None
        scores = matrix @ query_vector
        results: list[VectorSearchResult] = []
        for index, metadata_row in enumerate(metadata_rows):
            record_id = metadata_row["record_id"]
            if candidate_id_set is not None and record_id not in candidate_id_set:
                continue
            score = round(float(scores[index]), 6)
            if minimum_score is not None and score < minimum_score:
                continue
            results.append(
                VectorSearchResult(
                    record_id=record_id,
                    score=score,
                    metadata=dict(metadata_row.get("metadata") or {}),
                    document=str(metadata_row.get("document") or ""),
                )
            )
        return tuple(sorted(results, key=lambda result: (-result.score, result.record_id))[:top_k])

    def count(self) -> int:
        return len(self.load_metadata())

    def record_ids(self) -> set[str]:
        metadata_rows = self.load_metadata()
        vectors = self.load_vectors()
        if vectors.size == 0 or len(metadata_rows) != len(vectors):
            return set()
        return {row["record_id"] for row in metadata_rows}

    def load_records(self) -> tuple[VectorRecord, ...]:
        metadata_rows = self.load_metadata()
        matrix = self.load_vectors()
        if not metadata_rows or matrix.size == 0:
            return ()
        return tuple(
            VectorRecord(
                record_id=row["record_id"],
                embedding=matrix[index],
                metadata=dict(row.get("metadata") or {}),
                document=str(row.get("document") or ""),
            )
            for index, row in enumerate(metadata_rows)
        )

    def _load_cached(self) -> tuple[np.ndarray, list[dict]]:
        """Return (matrix, metadata) from in-memory cache, reloading if either file changed."""
        v_path = self.vectors_path
        m_path = self.metadata_path
        v_mtime = v_path.stat().st_mtime if v_path.exists() else 0.0
        m_mtime = m_path.stat().st_mtime if m_path.exists() else 0.0

        with _VECTOR_CACHE_LOCK:
            cached = _VECTOR_CACHE.get(v_path)
            if cached is not None:
                _, _, cached_v_mtime, cached_m_mtime = cached
                if cached_v_mtime == v_mtime and cached_m_mtime == m_mtime:
                    return cached[0], cached[1]

            matrix = (
                np.load(v_path).astype(np.float32)
                if v_path.exists()
                else np.empty((0, 0), dtype=np.float32)
            )
            metadata = (
                json.loads(m_path.read_text(encoding="utf-8"))
                if m_path.exists()
                else []
            )
            _VECTOR_CACHE[v_path] = (matrix, metadata, v_mtime, m_mtime)
            return matrix, metadata

    def _invalidate_cache(self) -> None:
        with _VECTOR_CACHE_LOCK:
            _VECTOR_CACHE.pop(self.vectors_path, None)

    def load_metadata(self) -> list[dict[str, Any]]:
        _, metadata = self._load_cached()
        return metadata

    def load_vectors(self) -> np.ndarray:
        matrix, _ = self._load_cached()
        return matrix


def write_faiss_index(index_path: Path, matrix: np.ndarray) -> None:
    try:
        import faiss
    except Exception:
        return
    if matrix.size == 0:
        return
    index = faiss.IndexFlatIP(matrix.shape[1])
    index.add(matrix)
    faiss.write_index(index, str(index_path))


def safe_collection_name(value: str) -> str:
    clean_value = re.sub(r"[^A-Za-z0-9_-]+", "_", value.strip())
    return clean_value.strip("_") or "students"
