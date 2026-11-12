from __future__ import annotations

import shutil
from pathlib import Path
from urllib.request import urlretrieve

from app.ai.config import (
    EMBEDDINGS_DIR,
    FACES_DIR,
    SFACE_MODELS_DIR,
    SFACE_MODEL_NAME,
    SFACE_MODEL_PATH,
    SFACE_MODEL_URL,
    TRAINING_MODELS_DIR,
    YUNET_MODELS_DIR,
    YUNET_MODEL_NAME,
    YUNET_MODEL_PATH,
    YUNET_MODEL_URL,
)


def ensure_ai_directories() -> None:
    YUNET_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    SFACE_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    FACES_DIR.mkdir(parents=True, exist_ok=True)
    EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)


def ensure_models() -> tuple[Path, Path]:
    ensure_ai_directories()
    yunet = _ensure_model(YUNET_MODEL_NAME, YUNET_MODEL_PATH, YUNET_MODEL_URL)
    sface = _ensure_model(SFACE_MODEL_NAME, SFACE_MODEL_PATH, SFACE_MODEL_URL)
    return yunet, sface


def _ensure_model(name: str, target: Path, url: str) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        return target
    source = TRAINING_MODELS_DIR / name
    if source.exists():
        shutil.copy2(source, target)
        return target
    print(f"Downloading AI model: {name}")
    urlretrieve(url, target)
    return target
