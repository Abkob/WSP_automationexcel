from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np


MODEL_NAME = "mixedbread-ai/mxbai-embed-large-v1"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_CONFIG_FILES = ("config.json",)
REQUIRED_WEIGHT_FILES = ("model.safetensors", "pytorch_model.bin")
REQUIRED_TOKENIZER_FILES = ("tokenizer.json", "tokenizer_config.json", "vocab.txt", "sentencepiece.bpe.model")
DOWNLOAD_PATTERNS = (
    "config.json",
    "model.safetensors",
    "tokenizer.json",
    "tokenizer_config.json",
    "vocab.txt",
    "special_tokens_map.json",
    "sentence_bert_config.json",
    "config_sentence_transformers.json",
    "modules.json",
    "1_Pooling/**",
    "2_Normalize/**",
    "README.md",
)


def snapshot_is_complete(snapshot: Path) -> bool:
    return (
        all((snapshot / name).is_file() for name in REQUIRED_CONFIG_FILES)
        and any((snapshot / name).is_file() for name in REQUIRED_WEIGHT_FILES)
        and any((snapshot / name).is_file() for name in REQUIRED_TOKENIZER_FILES)
    )


def clear_incomplete_cache_markers(hf_home: Path) -> None:
    repo_cache = hf_home / "hub" / ("models--" + MODEL_NAME.replace("/", "--"))
    marker_directory = repo_cache / ".no_exist"
    if not marker_directory.exists():
        return
    import shutil

    shutil.rmtree(marker_directory)


def local_model_directory(hf_home: Path) -> Path:
    return hf_home / "local_models" / MODEL_NAME.replace("/", "--")


def download_and_verify_model() -> dict[str, object]:
    hf_home = Path(os.environ.get("HF_HOME") or PROJECT_ROOT / ".models").resolve()
    hf_home.mkdir(parents=True, exist_ok=True)
    os.environ["HF_HOME"] = str(hf_home)
    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
    clear_incomplete_cache_markers(hf_home)

    from huggingface_hub import snapshot_download

    print(f"Downloading and repairing {MODEL_NAME} in {hf_home} (~669 MB)...")
    sys.stdout.flush()
    model_directory = local_model_directory(hf_home)
    model_directory.mkdir(parents=True, exist_ok=True)
    snapshot = Path(
        snapshot_download(
            repo_id=MODEL_NAME,
            # A regular local directory is intentional. Hugging Face's cache
            # layout relies on symlinks, which standard Windows accounts may
            # not be allowed to create (WinError 1314).
            local_dir=str(model_directory),
            allow_patterns=list(DOWNLOAD_PATTERNS),
            local_files_only=False,
            max_workers=4,
        )
    ).resolve()
    if not snapshot_is_complete(snapshot):
        raise RuntimeError(f"The downloaded model snapshot is incomplete: {snapshot}")

    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(str(snapshot), local_files_only=True)
    vectors = np.asarray(
        model.encode(
            [
                "Represent this sentence for searching relevant passages: student skilled in data analysis",
                "Student profile with Excel, SPSS, and research experience",
            ],
            normalize_embeddings=True,
            convert_to_numpy=True,
        ),
        dtype=np.float32,
    )
    if vectors.ndim != 2 or vectors.shape[0] != 2 or vectors.shape[1] <= 0:
        raise RuntimeError(f"The offline model returned an invalid shape: {vectors.shape}")
    if not np.isfinite(vectors).all():
        raise RuntimeError("The offline model returned non-finite embedding values.")

    result = {
        "model": MODEL_NAME,
        "snapshot": str(snapshot),
        "dimensions": int(vectors.shape[1]),
        "verified_at": datetime.now(UTC).isoformat(),
        "verification": "passed",
    }
    (hf_home / "model_install.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main() -> int:
    result = download_and_verify_model()
    print(f"Done. Offline query/document embedding check passed ({result['dimensions']} dimensions).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
