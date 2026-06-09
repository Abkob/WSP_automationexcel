from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_required_project_files_exist() -> None:
    required_files = [
        "TASK_CHECKLIST.md",
        "README.md",
        "requirements.txt",
        "pyproject.toml",
        "main.py",
        "config.py",
    ]

    for relative_path in required_files:
        assert (PROJECT_ROOT / relative_path).exists(), relative_path


def test_required_source_directories_exist() -> None:
    required_directories = [
        "app",
        "app/pages",
        "app/components",
        "database",
        "services",
        "tests",
        "tests/fixtures",
        "data/incoming_excel",
        "data/archive/original_excels",
        "data/backups",
        "data/exports",
        "data/logs",
        "data/semantic_index",
    ]

    for relative_path in required_directories:
        path = PROJECT_ROOT / relative_path
        assert path.exists(), relative_path
        assert path.is_dir(), relative_path

