from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Protocol, Sequence

import numpy as np

from config import AppSettings


class EmbeddingModelUnavailable(RuntimeError):
    """Raised when the configured local embedding model cannot be loaded."""


class EmbeddingModel(Protocol):
    model_name: str

    def encode(self, texts: Sequence[str], *, kind: str) -> np.ndarray:
        """Return one normalized vector per text."""


class SentenceTransformerEmbeddingModel:
    def __init__(self, model_name: str, *, local_files_only: bool = True) -> None:
        self.model_name = model_name
        self.local_files_only = local_files_only
        self._model = None
        self._load_error: EmbeddingModelUnavailable | None = None

    def encode(self, texts: Sequence[str], *, kind: str) -> np.ndarray:
        if kind not in {"document", "query"}:
            raise ValueError("Embedding kind must be 'document' or 'query'")
        clean_texts = [prepare_embedding_text(text, kind=kind, model_name=self.model_name) for text in texts]
        if not clean_texts:
            return np.empty((0, 0), dtype=np.float32)
        try:
            vectors = self.model.encode(clean_texts, normalize_embeddings=True, convert_to_numpy=True)
        except Exception as exc:  # pragma: no cover - exact backend exception depends on local install/cache.
            raise EmbeddingModelUnavailable(f"Could not encode text with {self.model_name!r}: {exc}") from exc
        return normalize_embedding_matrix(np.asarray(vectors, dtype=np.float32))

    @property
    def model(self):
        if self._load_error is not None:
            raise self._load_error
        if self._model is None:
            if self.local_files_only and not is_sentence_transformer_model_cached(self.model_name):
                raise EmbeddingModelUnavailable(
                    f"Embedding model {self.model_name!r} is not fully cached locally. "
                    "Cache it before offline semantic search, or the app will use text match fallback."
                )
            try:
                from sentence_transformers import SentenceTransformer
            except Exception as exc:  # pragma: no cover - covered by orchestration fallback tests.
                self._load_error = EmbeddingModelUnavailable("sentence-transformers is not installed or could not be imported.")
                raise self._load_error from exc
            try:
                self._model = SentenceTransformer(self.model_name, local_files_only=self.local_files_only)
            except Exception as exc:  # pragma: no cover - model cache/network availability is environment-specific.
                self._load_error = EmbeddingModelUnavailable(f"Could not load embedding model {self.model_name!r}: {exc}")
                raise self._load_error from exc
        return self._model


@lru_cache(maxsize=4)
def get_cached_sentence_transformer_model(model_name: str, local_files_only: bool) -> SentenceTransformerEmbeddingModel:
    return SentenceTransformerEmbeddingModel(model_name, local_files_only=local_files_only)


def get_default_embedding_model(settings: AppSettings) -> EmbeddingModel:
    return get_cached_sentence_transformer_model(settings.embedding_model_name, settings.embedding_local_files_only)


def prepare_embedding_text(text: str, *, kind: str, model_name: str) -> str:
    clean_text = " ".join(str(text).strip().split())
    if not clean_text:
        clean_text = "empty profile"
    if is_e5_model(model_name):
        prefix = "query" if kind == "query" else "passage"
        return f"{prefix}: {clean_text}"
    if is_mxbai_model(model_name):
        if kind == "query":
            return f"Represent this sentence for searching relevant passages: {clean_text}"
        return clean_text
    return clean_text


def is_e5_model(model_name: str) -> bool:
    return "e5" in model_name.casefold()


def is_mxbai_model(model_name: str) -> bool:
    return "mxbai" in model_name.casefold()


def normalize_embedding_matrix(vectors: np.ndarray) -> np.ndarray:
    matrix = np.asarray(vectors, dtype=np.float32)
    if matrix.ndim == 1:
        matrix = matrix.reshape(1, -1)
    if matrix.size == 0:
        return matrix.astype(np.float32)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return (matrix / norms).astype(np.float32)


def is_sentence_transformer_model_cached(model_name: str) -> bool:
    local_path = Path(model_name)
    if local_path.exists():
        return local_sentence_transformer_path_is_complete(local_path)
    installed_local_path = installed_local_model_path(model_name)
    if local_sentence_transformer_path_is_complete(installed_local_path):
        return True
    has_config = cached_file_exists(model_name, "config.json")
    has_weight = any(cached_file_exists(model_name, filename) for filename in ("model.safetensors", "pytorch_model.bin"))
    has_tokenizer = any(
        cached_file_exists(model_name, filename)
        for filename in ("tokenizer.json", "tokenizer_config.json", "vocab.txt", "sentencepiece.bpe.model")
    )
    return has_config and has_weight and has_tokenizer


def installed_local_model_path(model_name: str) -> Path:
    """Return the installer-managed, symlink-free model location."""
    import os

    hf_home = Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface"))
    return hf_home / "local_models" / model_name.replace("/", "--")


def resolve_sentence_transformer_source(model_name: str) -> str | Path:
    """Prefer an explicit or installer-managed local model before a Hub ID."""
    explicit_path = Path(model_name)
    if explicit_path.exists():
        return explicit_path
    installed_path = installed_local_model_path(model_name)
    if local_sentence_transformer_path_is_complete(installed_path):
        return installed_path
    return model_name


def local_sentence_transformer_path_is_complete(model_path: Path) -> bool:
    return (
        (model_path / "config.json").exists()
        and any((model_path / filename).exists() for filename in ("model.safetensors", "pytorch_model.bin"))
        and any((model_path / filename).exists() for filename in ("tokenizer.json", "tokenizer_config.json", "vocab.txt", "sentencepiece.bpe.model"))
    )


def cached_file_exists(model_name: str, filename: str) -> bool:
    # First try huggingface_hub's official lookup (works when blobs are properly linked).
    try:
        from huggingface_hub import try_to_load_from_cache
        cached_path = try_to_load_from_cache(model_name, filename)
        if isinstance(cached_path, str) and Path(cached_path).exists():
            return True
    except Exception:
        pass

    # On Windows, huggingface_hub stores files directly in the snapshot directory
    # rather than as symlinks into blobs, so try_to_load_from_cache returns None.
    # Fall back to scanning the snapshots directory directly.
    return _find_in_hf_cache_snapshots(model_name, filename)


def _find_in_hf_cache_snapshots(model_name: str, filename: str) -> bool:
    try:
        import os
        cache_home = Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface")) / "hub"
        # model_name is e.g. "mixedbread-ai/mxbai-embed-large-v1"
        repo_dir_name = "models--" + model_name.replace("/", "--")
        snapshots_dir = cache_home / repo_dir_name / "snapshots"
        if not snapshots_dir.exists():
            return False
        for snapshot in snapshots_dir.iterdir():
            if snapshot.is_dir() and (snapshot / filename).exists():
                return True
        return False
    except Exception:
        return False
