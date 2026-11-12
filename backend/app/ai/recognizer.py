from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


class SFaceRecognizer:
    def __init__(self, model_path: Path) -> None:
        model_buffer = np.frombuffer(model_path.read_bytes(), dtype=np.uint8)
        empty_config = np.empty((0,), dtype=np.uint8)
        self._recognizer = cv2.FaceRecognizerSF.create(
            "onnx",
            model_buffer,
            empty_config,
        )

    def embed(self, frame: np.ndarray, face_raw: np.ndarray) -> np.ndarray:
        aligned = self._recognizer.alignCrop(frame, face_raw)
        return self._recognizer.feature(aligned)
