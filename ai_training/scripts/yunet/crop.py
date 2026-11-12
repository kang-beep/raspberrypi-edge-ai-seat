from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from config import CROP_FILE_NAME, CROP_PADDING_RATIO, CROPS_DIR
from detector import FaceDetection


def select_best_face(faces: list[FaceDetection]) -> FaceDetection | None:
    if not faces:
        return None
    return max(faces, key=lambda face: face.score * face.width * face.height)


def crop_face(frame: np.ndarray, face: FaceDetection) -> np.ndarray:
    height, width = frame.shape[:2]
    pad_x = int(face.width * CROP_PADDING_RATIO)
    pad_y = int(face.height * CROP_PADDING_RATIO)

    x1 = max(0, face.x - pad_x)
    y1 = max(0, face.y - pad_y)
    x2 = min(width, face.x + face.width + pad_x)
    y2 = min(height, face.y + face.height + pad_y)
    return frame[y1:y2, x1:x2].copy()


def save_face_crop(frame: np.ndarray, faces: list[FaceDetection]) -> Path | None:
    face = select_best_face(faces)
    if face is None:
        print("No face detected on exit. Crop was not saved.")
        return None

    crop = crop_face(frame, face)
    if crop.size == 0:
        print("Face crop was empty. Crop was not saved.")
        return None

    CROPS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = CROPS_DIR / CROP_FILE_NAME
    _write_image(output_path, crop)
    print(f"Saved face crop: {output_path}")
    return output_path


def _write_image(path: Path, image: np.ndarray) -> None:
    ok, encoded = cv2.imencode(".jpg", image)
    if not ok:
        raise RuntimeError("Failed to encode face crop as JPEG")
    path.write_bytes(encoded.tobytes())
