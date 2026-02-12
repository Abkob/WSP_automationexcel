"""
Student Admissions Manager - Installer & Launcher
Handles everything in one file:
  1. Auto-installs missing Python dependencies
  2. Creates a desktop shortcut (Windows / Linux / macOS)
  3. Launches the application
"""

import subprocess
import sys
import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_SCRIPT = os.path.join(APP_DIR, "main.py")
MARKER_FILE = os.path.join(APP_DIR, ".installed")

REQUIRED_PACKAGES = [
    ("PyQt5", "PyQt5>=5.15.0"),
    ("pandas", "pandas>=1.3.0"),
    ("numpy", "numpy>=1.21.0"),
    ("openpyxl", "openpyxl>=3.0.9"),
]


# ─── Dependency installation ─────────────────────────────────────────────────

def _check_package(import_name: str) -> bool:
    """Return True if a package can be imported."""
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False


def install_dependencies() -> bool:
    """Install any missing packages. Returns True if everything is available."""
    missing = [
        pip_spec for import_name, pip_spec in REQUIRED_PACKAGES
        if not _check_package(import_name)
    ]

    if not missing:
        return True

    print(f"Installing {len(missing)} missing package(s): {', '.join(missing)}")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--quiet"] + missing,
        )
        print("All dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError as exc:
        print(f"pip install failed (exit code {exc.returncode}).")
        print("Please install manually:  pip install " + " ".join(missing))
        return False


# ─── Desktop shortcut creation ────────────────────────────────────────────────

def _create_windows_shortcut() -> bool:
    """Create a Windows .lnk shortcut on the desktop."""
    try:
        # Use powershell to create the shortcut (no extra pip packages needed)
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        if not os.path.isdir(desktop):
            desktop = os.path.join(
                os.environ.get("USERPROFILE", os.path.expanduser("~")),
                "Desktop",
            )
        shortcut_path = os.path.join(desktop, "Student Admissions.lnk")
        icon_path = os.path.join(APP_DIR, "logo.ico")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(APP_DIR, "logo.png")
        icon_clause = f"$s.IconLocation = '{icon_path}'" if os.path.exists(icon_path) else ""

        ps_script = (
            "$ws = New-Object -ComObject WScript.Shell; "
            f"$s = $ws.CreateShortcut('{shortcut_path}'); "
            f"$s.TargetPath = '{sys.executable}'; "
            f"$s.Arguments = '\"{MAIN_SCRIPT}\"'; "
            f"$s.WorkingDirectory = '{APP_DIR}'; "
            f"$s.Description = 'Student Admissions Manager'; "
            f"{icon_clause}; "
            "$s.Save()"
        )
        subprocess.check_call(
            ["powershell", "-NoProfile", "-Command", ps_script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"Desktop shortcut created: {shortcut_path}")
        return True
    except Exception as exc:
        print(f"Could not create Windows shortcut: {exc}")
        return False


def _create_linux_shortcut() -> bool:
    """Create a .desktop entry on Linux."""
    try:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        if not os.path.isdir(desktop):
            desktop = os.path.join(
                os.path.expanduser("~"), ".local", "share", "applications"
            )
            os.makedirs(desktop, exist_ok=True)

        shortcut_path = os.path.join(desktop, "student-admissions.desktop")
        content = (
            "[Desktop Entry]\n"
            "Version=1.0\n"
            "Type=Application\n"
            "Name=Student Admissions Manager\n"
            "Comment=Manage student admissions data\n"
            f"Exec={sys.executable} \"{MAIN_SCRIPT}\"\n"
            f"Path={APP_DIR}\n"
            "Terminal=false\n"
            "Categories=Education;Office;\n"
        )
        with open(shortcut_path, "w") as fh:
            fh.write(content)
        os.chmod(shortcut_path, 0o755)
        print(f"Desktop shortcut created: {shortcut_path}")
        return True
    except Exception as exc:
        print(f"Could not create Linux shortcut: {exc}")
        return False


def _create_mac_shortcut() -> bool:
    """Create a .command launcher on macOS."""
    try:
        shortcut_path = os.path.join(
            os.path.expanduser("~"), "Desktop", "Student Admissions.command"
        )
        content = (
            "#!/bin/bash\n"
            f'cd "{APP_DIR}"\n'
            f'{sys.executable} main.py\n'
        )
        with open(shortcut_path, "w") as fh:
            fh.write(content)
        os.chmod(shortcut_path, 0o755)
        print(f"Desktop shortcut created: {shortcut_path}")
        return True
    except Exception as exc:
        print(f"Could not create macOS shortcut: {exc}")
        return False


def create_shortcut() -> bool:
    """Create a platform-appropriate desktop shortcut."""
    if sys.platform == "win32":
        return _create_windows_shortcut()
    elif sys.platform == "darwin":
        return _create_mac_shortcut()
    else:
        return _create_linux_shortcut()


# ─── Admin elevation (Windows only) ──────────────────────────────────────────

def _is_admin() -> bool:
    if sys.platform != "win32":
        return True
    try:
        import ctypes
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    os.chdir(APP_DIR)

    print("=" * 60)
    print("  Student Admissions Manager - Setup & Launch")
    print("=" * 60)
    print()

    # Step 1 - Dependencies
    print("[1/3] Checking dependencies...")
    if not install_dependencies():
        input("\nPress Enter to exit...")
        return 1

    # Step 2 - Desktop shortcut (only on first run)
    already_installed = os.path.exists(MARKER_FILE)
    if not already_installed:
        print("[2/3] Creating desktop shortcut...")
        create_shortcut()
        # Write marker so we skip the shortcut step next time
        try:
            with open(MARKER_FILE, "w") as fh:
                fh.write("installed")
        except OSError:
            pass
    else:
        print("[2/3] Shortcut already exists, skipping.")

    # Step 3 - Launch
    print("[3/3] Launching application...")
    print()
    subprocess.run([sys.executable, MAIN_SCRIPT])
    return 0


if __name__ == "__main__":
    sys.exit(main())
