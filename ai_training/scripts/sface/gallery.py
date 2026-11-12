from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from config import GALLERY_DIR, GALLERY_IMAGE_EXTENSIONS
from recognizer import SFaceRecognizer
from yunet_bridge import load_yunet_api


def load_gallery(recognizer: SFaceRecognizer) -> dict[str, np.ndarray]:
    GALLERY_DIR.mkdir(parents=True, exist_ok=True)
    image_paths = sorted(
        path
        for path in GALLERY_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in GALLERY_IMAGE_EXTENSIONS
    )
    if not image_paths:
        print(f"No gallery images found in {GALLERY_DIR}")
        return {}

    ensure_yunet_model, YuNetDetector = load_yunet_api()
    yunet = YuNetDetector(ensure_yunet_model(), (320, 320))
    gallery: dict[str, np.ndarray] = {}
    for image_path in image_paths:
        embedding = _embed_gallery_image(yunet, recognizer, image_path)
        if embedding is None:
            continue
        gallery[image_path.stem] = embedding
        print(f"Enrolled gallery face: {image_path.name}")
    return gallery


def _embed_gallery_image(
    yunet: object,
    recognizer: SFaceRecognizer,
    image_path: Path,
) -> np.ndarray | None:
    image = _read_image(image_path)
    if image is None:
        print(f"Failed to read gallery image: {image_path}")
        return None

    yunet.set_input_size(image.shape[1], image.shape[0])
    faces = yunet.detect(image)
    if not faces:
        print(f"No face found in gallery image: {image_path.name}")
        return None

    best = max(faces, key=lambda face: face.score * face.width * face.height)
    return recognizer.embed(image, best.raw)


def _read_image(path: Path) -> np.ndarray | None:
    data = np.frombuffer(path.read_bytes(), dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)
