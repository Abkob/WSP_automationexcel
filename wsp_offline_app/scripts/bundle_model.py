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


def model_is_complete(path: Path) -> bool:
    return (
        (path / "config.json").is_file()
        and any((path / name).is_file() for name in ("model.safetensors", "pytorch_model.bin"))
        and any((path / name).is_file() for name in ("tokenizer.json", "tokenizer_config.json", "vocab.txt"))
    )


def find_model_source() -> Path:
    import os
    hf_home = os.environ.get("HF_HOME")
    homes = [Path(hf_home)] if hf_home else []
    homes.extend([
        Path.home() / ".cache" / "huggingface",
        Path("C:/Users") / Path.home().name / ".cache" / "huggingface",
    ])
    slug = MODEL_NAME.replace("/", "--")
    for home in homes:
        local_model = home / "local_models" / slug
        if model_is_complete(local_model):
            return local_model
        snapshots = home / "hub" / f"models--{slug}" / "snapshots"
        if snapshots.is_dir():
            for snapshot in snapshots.iterdir():
                if snapshot.is_dir() and model_is_complete(snapshot):
                    return snapshot
    raise FileNotFoundError(
        "A complete Hugging Face model installation was not found. "
        "Run the app once (with internet) to download the model, then try again."
    )


def bundle_model() -> None:
    folder_name = MODEL_NAME.replace("/", "--")
    dest = PROJECT_ROOT / ".models" / "local_models" / folder_name
    dest.parent.mkdir(parents=True, exist_ok=True)

    try:
        src = find_model_source()
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

    size_mb = sum(f.stat().st_size for f in src.rglob("*") if f.is_file()) / 1_048_576
    action = "Repairing" if dest.exists() else "Copying"
    print(f"{action} {MODEL_NAME} ({size_mb:.0f} MB) in .models/ ...")
    shutil.copytree(str(src), str(dest), dirs_exist_ok=True)
    print(f"Done. Model bundled at:\n  {dest}")
    print()
    print("The app will now use the bundled model on any machine this folder is copied to.")


if __name__ == "__main__":
    bundle_model()
