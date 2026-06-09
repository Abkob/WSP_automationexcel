from __future__ import annotations

from pathlib import Path

import pytest

from config import AppSettings, ensure_data_directories, get_default_settings, get_testing_settings


def test_default_settings_resolve_inside_project() -> None:
    settings = get_default_settings()

    assert settings.app_name == "WSP Offline System"
    assert settings.project_root.exists()
    assert settings.data_dir == settings.project_root / "data"
    assert settings.database_path == settings.data_dir / "wsp.db"
    assert settings.runtime_mode == "development"
    assert settings.native_mode is False
    assert settings.ui_host == "127.0.0.1"
    assert settings.ui_port == 8080


def test_testing_settings_use_supplied_data_dir(tmp_path: Path) -> None:
    settings = get_testing_settings(tmp_path)

    assert settings.runtime_mode == "testing"
    assert settings.data_dir == tmp_path.resolve()
    assert settings.database_path == tmp_path.resolve() / "wsp.db"


def test_native_mode_flag_can_be_read_without_starting_ui(tmp_path: Path) -> None:
    settings = AppSettings(data_dir=tmp_path, runtime_mode="testing", native_mode=True)

    assert settings.native_mode is True


def test_semantic_ollama_settings_have_local_defaults(tmp_path: Path) -> None:
    settings = AppSettings(data_dir=tmp_path, runtime_mode="testing")

    assert settings.semantic_search_enabled is True
    assert settings.embedding_model_name == "mixedbread-ai/mxbai-embed-large-v1"
    assert settings.embedding_local_files_only is True
    assert settings.semantic_vector_store_backend == "faiss"
    assert settings.rag_candidate_limit == 60
    assert settings.rag_profile_text_limit == 180
    assert settings.ollama_base_url == "http://localhost:11434"
    assert settings.ollama_model_name == "gemma3:4b"
    assert settings.ollama_request_timeout_seconds == 90.0


def test_semantic_ollama_settings_can_be_overridden(tmp_path: Path) -> None:
    settings = AppSettings(
        data_dir=tmp_path,
        runtime_mode="testing",
        semantic_search_enabled=True,
        ollama_base_url="http://localhost:11435",
        ollama_model_name="custom-model",
        ollama_request_timeout_seconds=5.0,
    )

    assert settings.semantic_search_enabled is True
    assert settings.ollama_base_url == "http://localhost:11435"
    assert settings.ollama_model_name == "custom-model"
    assert settings.ollama_request_timeout_seconds == 5.0


def test_ensure_data_directories_creates_all_required_directories(tmp_path: Path) -> None:
    settings = AppSettings(data_dir=tmp_path / "data", runtime_mode="testing")

    created = ensure_data_directories(settings)

    assert created == settings.required_directories
    for directory in settings.required_directories:
        assert directory.exists()
        assert directory.is_dir()


def test_ensure_data_directories_is_idempotent(tmp_path: Path) -> None:
    settings = AppSettings(data_dir=tmp_path / "data", runtime_mode="testing")

    first = ensure_data_directories(settings)
    second = ensure_data_directories(settings)

    assert first == second


def test_ensure_data_directories_logs_new_directories(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    settings = AppSettings(data_dir=tmp_path / "data", runtime_mode="testing")
    caplog.set_level("INFO", logger="config")

    ensure_data_directories(settings)

    assert "Created data directory" in caplog.text


def test_ensure_data_directories_rejects_file_where_directory_is_expected(tmp_path: Path) -> None:
    data_path = tmp_path / "data"
    data_path.write_text("not a directory", encoding="utf-8")
    settings = AppSettings(data_dir=data_path, runtime_mode="testing")

    with pytest.raises(NotADirectoryError, match="not a directory"):
        ensure_data_directories(settings)


def test_invalid_runtime_mode_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Invalid runtime_mode"):
        AppSettings(data_dir=tmp_path, runtime_mode="invalid")
