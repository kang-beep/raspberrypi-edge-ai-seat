from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from app.ai.config import DATA_ROOT, EMBEDDINGS_DIR, FACES_DIR


def save_enrollment_artifacts(
    user_id: int,
    crop_bgr: np.ndarray,
    embedding: np.ndarray,
) -> tuple[str, str]:
    FACES_DIR.mkdir(parents=True, exist_ok=True)
    EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)

    image_path = FACES_DIR / f"user_{user_id}.jpg"
    embedding_path = EMBEDDINGS_DIR / f"user_{user_id}.npy"
    _write_jpeg(image_path, crop_bgr)
    np.save(embedding_path, embedding.astype(np.float32))
    return (
        _to_relative(image_path),
        _to_relative(embedding_path),
    )


def delete_enrollment_artifacts(
    image_rel_path: str | None,
    embedding_rel_path: str | None,
) -> None:
    _delete_data_file(image_rel_path)
    _delete_data_file(embedding_rel_path)


def _delete_data_file(relative_path: str | None) -> None:
    if not relative_path:
        return
    candidate = (DATA_ROOT / relative_path).resolve()
    try:
        candidate.relative_to(DATA_ROOT.resolve())
    except ValueError:
        return
    if candidate.is_file():
        candidate.unlink()


def _write_jpeg(path: Path, image: np.ndarray) -> None:
    ok, encoded = cv2.imencode(".jpg", image)
    if not ok:
        raise RuntimeError("Failed to encode face crop")
    path.write_bytes(encoded.tobytes())


def _to_relative(path: Path) -> str:
    return path.resolve().relative_to(DATA_ROOT.resolve()).as_posix()
