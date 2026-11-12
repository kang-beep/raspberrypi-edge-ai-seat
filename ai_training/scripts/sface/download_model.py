from __future__ import annotations

from pathlib import Path
from urllib.request import urlretrieve

from config import MODELS_DIR, SFACE_MODEL_PATH, SFACE_MODEL_URL


def ensure_sface_model() -> Path:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    if SFACE_MODEL_PATH.exists():
        return SFACE_MODEL_PATH

    print(f"Downloading SFace model to {SFACE_MODEL_PATH}")
    urlretrieve(SFACE_MODEL_URL, SFACE_MODEL_PATH)
    return SFACE_MODEL_PATH


if __name__ == "__main__":
    model_path = ensure_sface_model()
    print(f"Ready: {model_path}")
