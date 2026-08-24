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


def test_one_click_installer_uses_branded_graphical_setup() -> None:
    launcher = (PROJECT_ROOT / "INSTALL_WSP.bat").read_text(encoding="utf-8")
    installer = (PROJECT_ROOT / "scripts" / "install_gui.ps1").read_text(encoding="utf-8")

    assert "install_gui.ps1" in launcher
    assert "-WindowStyle Hidden" in launcher
    assert "aub-logo-horizontal.png" in installer
    assert "Desktop and Start Menu shortcuts" in installer
    assert "Launch WSP" in installer
    assert "download_mxbai.py" in (PROJECT_ROOT / "scripts" / "install.ps1").read_text(encoding="utf-8")
    install_script = (PROJECT_ROOT / "scripts" / "install.ps1").read_text(encoding="utf-8")
    assert "Assert-AppShortcut" in install_script
    assert "Start-And-VerifyApplication" in install_script
    assert "/api/system-status" in install_script
    assert "private Python environment" in install_script
    assert "Offline query/document embedding check passed" in (
        PROJECT_ROOT / "scripts" / "download_mxbai.py"
    ).read_text(encoding="utf-8")


def test_launcher_self_redirects_to_the_private_runtime() -> None:
    launcher = (PROJECT_ROOT / "wsp_launcher.pyw").read_text(encoding="utf-8")

    assert "_redirect_to_private_runtime" in launcher
    assert "sys.prefix" in launcher
    assert 'APP_DIR / ".venv" / "Scripts" / "pythonw.exe"' in launcher
    assert '"WSP Offline System" / "wsp_offline_app"' in launcher
