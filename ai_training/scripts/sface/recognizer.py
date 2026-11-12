from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from config import COSINE_THRESHOLD


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

    def cosine_similarity(self, left: np.ndarray, right: np.ndarray) -> float:
        return float(
            self._recognizer.match(
                left,
                right,
                cv2.FaceRecognizerSF_FR_COSINE,
            )
        )

    def best_match(
        self,
        query: np.ndarray,
        gallery: dict[str, np.ndarray],
    ) -> tuple[str, float]:
        best_name = "Unknown"
        best_score = -1.0
        for name, embedding in gallery.items():
            score = self.cosine_similarity(query, embedding)
            if score > best_score:
                best_name = name
                best_score = score

        if best_score < COSINE_THRESHOLD:
            return "Unknown", best_score
        return best_name, best_score
