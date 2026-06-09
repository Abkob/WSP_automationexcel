from __future__ import annotations

import numpy as np

from services.embedding_service import is_sentence_transformer_model_cached, normalize_embedding_matrix, prepare_embedding_text


def test_e5_embedding_text_uses_query_and_passage_prefixes() -> None:
    model_name = "intfloat/multilingual-e5-small"

    assert prepare_embedding_text(" spreadsheet cleanup ", kind="query", model_name=model_name) == "query: spreadsheet cleanup"
    assert prepare_embedding_text(" Excel profile ", kind="document", model_name=model_name) == "passage: Excel profile"


def test_non_e5_embedding_text_does_not_add_prefix() -> None:
    assert prepare_embedding_text("  admin   assistant  ", kind="query", model_name="sentence-transformers/all-MiniLM-L6-v2") == "admin assistant"


def test_normalize_embedding_matrix_returns_unit_vectors() -> None:
    matrix = normalize_embedding_matrix(np.array([[3.0, 4.0], [0.0, 0.0]], dtype=np.float32))

    assert np.allclose(matrix[0], np.array([0.6, 0.8], dtype=np.float32))
    assert np.allclose(matrix[1], np.array([0.0, 0.0], dtype=np.float32))


def test_sentence_transformer_cache_check_requires_config_weight_and_tokenizer(monkeypatch) -> None:
    cached_files = {"config.json", "model.safetensors", "tokenizer.json"}

    def fake_cached_file_exists(_model_name: str, filename: str) -> bool:
        return filename in cached_files

    monkeypatch.setattr("services.embedding_service.cached_file_exists", fake_cached_file_exists)

    assert is_sentence_transformer_model_cached("intfloat/multilingual-e5-small") is True
    cached_files.remove("model.safetensors")
    assert is_sentence_transformer_model_cached("intfloat/multilingual-e5-small") is False
