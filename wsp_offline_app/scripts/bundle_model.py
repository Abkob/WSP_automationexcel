"""
Copy the mxbai embedding model from the HuggingFace cache into .models/
so the whole app folder is self-contained and portable.

Run once on the development machine (where the model is already cached):
    .venv\\Scripts\\python scripts\\bundle_model.py

After this script completes, the app will use .models/ instead of
~/.cache/huggingface/ on any machine it is copied to.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_NAME = "mixedbread-ai/mxbai-embed-large-v1"


def find_hf_cache() -> Path:
    import os
    hf_home = os.environ.get("HF_HOME")
    if hf_home:
        candidate = Path(hf_home) / "hub"
        if candidate.exists():
            return candidate
    for candidate in [
        Path.home() / ".cache" / "huggingface" / "hub",
        Path("C:/Users") / Path.home().name / ".cache" / "huggingface" / "hub",
    ]:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "HuggingFace hub cache not found. "
        "Run the app once (with internet) to download the model, then try again."
    )


def bundle_model() -> None:
    dest_hub = PROJECT_ROOT / ".models" / "hub"
    dest_hub.mkdir(parents=True, exist_ok=True)

    folder_name = "models--" + MODEL_NAME.replace("/", "--")

    try:
        src_hub = find_hf_cache()
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

    src = src_hub / folder_name
    if not src.exists():
        print(f"ERROR: Model folder not found at {src}")
        print(
            "Make sure you have run the WSP app at least once with internet access "
            "so the model is downloaded to the HuggingFace cache."
        )
        sys.exit(1)

    dest = dest_hub / folder_name
    if dest.exists():
        print(f"Model already bundled at:\n  {dest}")
        print("Nothing to do. Delete .models/ and re-run to force a fresh copy.")
        return

    size_mb = sum(f.stat().st_size for f in src.rglob("*") if f.is_file()) / 1_048_576
    print(f"Copying {MODEL_NAME} ({size_mb:.0f} MB) into .models/ ...")
    shutil.copytree(str(src), str(dest))
    print(f"Done. Model bundled at:\n  {dest}")
    print()
    print("The app will now use the bundled model on any machine this folder is copied to.")


if __name__ == "__main__":
    bundle_model()
