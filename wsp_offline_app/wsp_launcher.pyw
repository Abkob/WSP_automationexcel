from __future__ import annotations

import ctypes
import io
import logging
import os
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

# ── Anchor everything to the folder this file lives in ──────────────────────
APP_DIR = Path(__file__).resolve().parent


def _same_path(left: Path | str, right: Path | str) -> bool:
    try:
        return Path(left).resolve() == Path(right).resolve()
    except (OSError, RuntimeError, ValueError):
        return os.path.normcase(os.path.abspath(str(left))) == os.path.normcase(os.path.abspath(str(right)))


def _private_runtime_candidate() -> tuple[Path, Path] | None:
    """Return the verified app-local pythonw and launcher when available.

    The first candidate repairs a launcher opened directly from its installed or
    development folder. The second makes an accidentally opened extracted copy
    redirect to the canonical Local AppData installation.
    """
    local_pythonw = APP_DIR / ".venv" / "Scripts" / "pythonw.exe"
    local_launcher = APP_DIR / "wsp_launcher.pyw"
    if local_pythonw.is_file() and local_launcher.is_file():
        return local_pythonw, local_launcher

    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        installed_dir = Path(local_app_data) / "WSP Offline System" / "wsp_offline_app"
        installed_pythonw = installed_dir / ".venv" / "Scripts" / "pythonw.exe"
        installed_launcher = installed_dir / "wsp_launcher.pyw"
        if installed_pythonw.is_file() and installed_launcher.is_file():
            return installed_pythonw, installed_launcher
    return None


def _redirect_to_private_runtime() -> bool:
    candidate = _private_runtime_candidate()
    if candidate is None:
        return False
    pythonw, launcher = candidate
    # On Windows the venv executable may resolve to the base Python binary, so
    # sys.executable alone is not reliable. sys.prefix identifies the active
    # environment and must match the .venv that owns the selected pythonw.
    expected_prefix = pythonw.parent.parent
    if _same_path(sys.prefix, expected_prefix) and _same_path(APP_DIR / "wsp_launcher.pyw", launcher):
        return False
    try:
        subprocess.Popen(
            [str(pythonw), str(launcher)],
            cwd=str(launcher.parent),
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except OSError as exc:
        log.error("Could not redirect to private runtime %s: %s", pythonw, exc)
        return False
    log.info("Redirected launcher from %s to private runtime %s", sys.executable, pythonw)
    return True

# ── pythonw.exe sets stdout/stderr to None — redirect to null so any
#    library that calls sys.stdout.write() / .isatty() doesn't crash. ────────
if sys.stdout is None:
    sys.stdout = io.open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = io.open(os.devnull, "w", encoding="utf-8")

# ── Point HuggingFace cache to bundled .models/ only when it is complete ────
# This must happen before any sentence-transformers / huggingface_hub import.
def _bundled_embedding_cache_is_complete(cache_root: Path) -> bool:
    local_model = cache_root / "local_models" / "mixedbread-ai--mxbai-embed-large-v1"
    if local_model.is_dir():
        has_config = (local_model / "config.json").is_file()
        has_weights = any((local_model / name).is_file() for name in ("model.safetensors", "pytorch_model.bin"))
        has_tokenizer = any(
            (local_model / name).is_file()
            for name in ("tokenizer.json", "tokenizer_config.json", "vocab.txt", "sentencepiece.bpe.model")
        )
        if has_config and has_weights and has_tokenizer:
            return True
    snapshots = (
        cache_root
        / "hub"
        / "models--mixedbread-ai--mxbai-embed-large-v1"
        / "snapshots"
    )
    if not snapshots.is_dir():
        return False
    for snapshot in snapshots.iterdir():
        if not snapshot.is_dir():
            continue
        has_config = (snapshot / "config.json").is_file()
        has_weights = any((snapshot / name).is_file() for name in ("model.safetensors", "pytorch_model.bin"))
        has_tokenizer = any(
            (snapshot / name).is_file()
            for name in ("tokenizer.json", "tokenizer_config.json", "vocab.txt", "sentencepiece.bpe.model")
        )
        if has_config and has_weights and has_tokenizer:
            return True
    return False


_bundled_models = APP_DIR / ".models"
if _bundled_embedding_cache_is_complete(_bundled_models):
    os.environ["HF_HOME"] = str(_bundled_models)

# ── Logging (no console in .pyw — write to file instead) ────────────────────
_log_dir = APP_DIR / "data"
_log_dir.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=str(_log_dir / "launcher.log"),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)

# ── Ensure app imports resolve ───────────────────────────────────────────────
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

PORT = 8080
URL = f"http://127.0.0.1:{PORT}/"


# ────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────

def _is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def _wait_for_server(port: int, timeout: float = 45.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if _is_port_in_use(port):
            return True
        time.sleep(0.4)
    return False


def _fatal(msg: str) -> None:
    log.error(msg)
    ctypes.windll.user32.MessageBoxW(
        0,
        f"{msg}\n\nDetails: {_log_dir / 'launcher.log'}",
        "WSP — Startup Error",
        0x10,  # MB_ICONERROR
    )


def _make_tray_icon():
    """Return a 64×64 RGBA tray icon using the AUB seal from the static folder."""
    import numpy as np
    from PIL import Image

    logo_path = APP_DIR / "app" / "static" / "aub-logo-vertical.jpg"
    if not logo_path.exists():
        # Fallback: plain maroon circle
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        from PIL import ImageDraw
        ImageDraw.Draw(img).ellipse((2, 2, 62, 62), fill=(128, 0, 32))
        return img

    img = Image.open(logo_path).convert("RGBA")
    # Tight crop around the circular seal (pre-computed from image analysis)
    seal = img.crop((388, 49, 985, 647))

    # Make white background transparent
    arr = np.array(seal, dtype=np.uint8)
    white = (arr[:, :, 0] > 230) & (arr[:, :, 1] > 230) & (arr[:, :, 2] > 230)
    arr[white, 3] = 0
    seal = Image.fromarray(arr)

    return seal.resize((64, 64), Image.LANCZOS)


# ────────────────────────────────────────────────────────────────────────────
# Browser launcher — prefer an app window (no address bar / tabs)
# ────────────────────────────────────────────────────────────────────────────

def _open_app_window(url: str) -> None:
    """
    Open the URL in a dedicated app window.
    Priority: Chrome --app > Edge --app > Chrome --new-window >
              Edge --new-window > webbrowser.open_new (system default).
    --app mode gives a clean borderless window that looks like a native app.
    """
    import subprocess

    _BROWSER_CANDIDATES = [
        (r"C:\Program Files\Google\Chrome\Application\chrome.exe",          "--app="),
        (r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",    "--app="),
        (r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",         "--app="),
        (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",   "--app="),
        (r"C:\Program Files\Google\Chrome\Application\chrome.exe",          "--new-window"),
        (r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",    "--new-window"),
        (r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",         "--new-window"),
    ]

    for exe, flag in _BROWSER_CANDIDATES:
        if Path(exe).exists():
            arg = flag + url if flag.endswith("=") else flag
            args = [exe, arg, url] if flag == "--new-window" else [exe, arg]
            try:
                subprocess.Popen(args)
                log.info("Opened browser: %s %s", Path(exe).name, flag)
                return
            except Exception as exc:
                log.warning("Browser launch failed (%s): %s", exe, exc)

    # Last resort: let the OS pick
    webbrowser.open_new(url)
    log.info("Opened browser via webbrowser.open_new")


# ────────────────────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────────────────────

def main() -> None:
    # A .pyw file opened directly is normally handled by Windows' global Python.
    # Always move into WSP's verified private environment before importing deps.
    if _redirect_to_private_runtime():
        return

    # If WSP is already running, just open a new window and exit.
    if _is_port_in_use(PORT):
        log.info("Server already running — opening browser window")
        _open_app_window(URL)
        return

    log.info("Starting WSP Offline System on port %d", PORT)

    # ── Import app modules ────────────────────────────────────────────────
    try:
        import uvicorn
        from main import build_startup_context
        from app.web_app import create_web_app
    except Exception as exc:
        _fatal(f"Failed to import app modules:\n{exc}")
        return

    # ── Initialise DB / directories ───────────────────────────────────────
    try:
        context = build_startup_context()
        app = create_web_app(context.settings)
    except Exception as exc:
        _fatal(f"App initialisation failed:\n{exc}")
        return

    # ── Launch uvicorn in a daemon thread ─────────────────────────────────
    # log_config=None disables uvicorn's dictConfig setup which calls
    # sys.stdout.isatty() — that crashes under pythonw.exe where stdout is None.
    config = uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="warning", log_config=None)
    server = uvicorn.Server(config)
    server_thread = threading.Thread(target=server.run, daemon=True, name="wsp-server")
    server_thread.start()

    if not _wait_for_server(PORT, timeout=45.0):
        _fatal("Server did not become ready within 45 seconds.")
        server.should_exit = True
        return

    log.info("Server ready — opening browser window")
    _open_app_window(URL)

    # ── System tray icon ──────────────────────────────────────────────────
    try:
        import pystray
    except ImportError:
        log.warning("pystray not installed — running without tray icon (server stays up)")
        server_thread.join()
        return

    def on_open(icon, item):  # noqa: ARG001
        _open_app_window(URL)

    def on_exit(icon, item):  # noqa: ARG001
        log.info("Exit requested — shutting down")
        server.should_exit = True
        icon.stop()

    icon_image = _make_tray_icon()
    menu = pystray.Menu(
        pystray.MenuItem("Open WSP", on_open, default=True),
        pystray.MenuItem("Exit", on_exit),
    )
    tray = pystray.Icon("WSP Offline System", icon_image, "WSP Offline System", menu)

    log.info("Tray icon active")
    tray.run()  # blocks until on_exit calls icon.stop()
    log.info("Shutdown complete")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log.exception("Unhandled exception in launcher")
