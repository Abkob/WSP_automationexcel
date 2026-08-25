from __future__ import annotations

import argparse
import importlib
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def verify_imports() -> None:
    modules = (
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pandas",
        "openpyxl",
        "numpy",
        "faiss",
        "sentence_transformers",
        "PIL",
        "pystray",
    )
    for module_name in modules:
        importlib.import_module(module_name)


def verify_application() -> None:
    from config import AppSettings
    from main import build_startup_context
    from app.web_app import create_web_app

    settings = AppSettings(project_root=ROOT, runtime_mode="production")
    context = build_startup_context(settings)
    app = create_web_app(context.settings)
    route_paths = {getattr(route, "path", "") for route in app.routes}
    required_routes = {"/", "/filters", "/excel-sheets", "/student-profile", "/api/dashboard"}
    missing = sorted(required_routes - route_paths)
    if missing:
        raise RuntimeError(f"Application routes are missing: {', '.join(missing)}")

    marker = settings.data_dir / ".install_write_test"
    marker.write_text("ok", encoding="utf-8")
    marker.unlink()
    if not settings.database_path.exists():
        raise RuntimeError("The local SQLite database could not be initialized.")


def verify_model() -> None:
    model_directory = ROOT / ".models"
    os.environ["HF_HOME"] = str(model_directory)
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("mixedbread-ai/mxbai-embed-large-v1", local_files_only=True)
    vectors = model.encode(["installation verification"], normalize_embeddings=True)
    if getattr(vectors, "shape", (0, 0))[0] != 1 or vectors.shape[1] <= 0:
        raise RuntimeError("The offline model returned an invalid embedding.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a WSP Offline System installation.")
    parser.add_argument("--skip-model", action="store_true")
    args = parser.parse_args()

    print("[VERIFY] Required Python modules")
    verify_imports()
    print("[VERIFY] Database and web application")
    verify_application()
    if not args.skip_model:
        print("[VERIFY] Offline embedding model")
        verify_model()
    print("[VERIFY] Installation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
