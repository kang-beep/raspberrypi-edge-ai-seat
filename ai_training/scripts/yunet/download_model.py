from __future__ import annotations

from pathlib import Path
from urllib.request import urlretrieve

from config import MODELS_DIR, YUNET_MODEL_PATH, YUNET_MODEL_URL


def ensure_yunet_model() -> Path:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    if YUNET_MODEL_PATH.exists():
        return YUNET_MODEL_PATH

    print(f"Downloading YuNet model to {YUNET_MODEL_PATH}")
    urlretrieve(YUNET_MODEL_URL, YUNET_MODEL_PATH)
    return YUNET_MODEL_PATH


if __name__ == "__main__":
    model_path = ensure_yunet_model()
    print(f"Ready: {model_path}")
