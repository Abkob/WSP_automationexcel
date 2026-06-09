from __future__ import annotations

from pathlib import Path

from config import get_testing_settings
from main import StartupContext, build_startup_context


def test_build_startup_context_creates_data_directories(tmp_path: Path) -> None:
    settings = get_testing_settings(tmp_path / "runtime")

    context = build_startup_context(settings)

    assert isinstance(context, StartupContext)
    assert context.settings == settings
    assert len(context.created_directories) == len(settings.required_directories)
    for directory in settings.required_directories:
        assert directory.exists()
    assert settings.database_path.exists()
