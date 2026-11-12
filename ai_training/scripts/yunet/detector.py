from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from config import NMS_THRESHOLD, SCORE_THRESHOLD, TOP_K


@dataclass(frozen=True)
class FaceDetection:
    x: int
    y: int
    width: int
    height: int
    score: float
    right_eye: tuple[int, int]
    left_eye: tuple[int, int]
    nose: tuple[int, int]
    right_mouth: tuple[int, int]
    left_mouth: tuple[int, int]
    raw: np.ndarray


class YuNetDetector:
    def __init__(self, model_path: Path, input_size: tuple[int, int]) -> None:
        model_buffer = _load_model_buffer(model_path)
        empty_config = np.empty((0,), dtype=np.uint8)
        self._detector = cv2.FaceDetectorYN.create(
            "onnx",
            model_buffer,
            empty_config,
            input_size,
            SCORE_THRESHOLD,
            NMS_THRESHOLD,
            TOP_K,
        )

    def set_input_size(self, width: int, height: int) -> None:
        self._detector.setInputSize((width, height))

    def detect(self, frame: np.ndarray) -> list[FaceDetection]:
        _, faces = self._detector.detect(frame)
        if faces is None:
            return []
        return [self._to_detection(face) for face in faces]

    def _to_detection(self, face: np.ndarray) -> FaceDetection:
        return FaceDetection(
            x=int(face[0]),
            y=int(face[1]),
            width=int(face[2]),
            height=int(face[3]),
            score=float(face[14]),
            right_eye=(int(face[4]), int(face[5])),
            left_eye=(int(face[6]), int(face[7])),
            nose=(int(face[8]), int(face[9])),
            right_mouth=(int(face[10]), int(face[11])),
            left_mouth=(int(face[12]), int(face[13])),
            raw=np.asarray(face, dtype=np.float32),
        )


def _load_model_buffer(model_path: Path) -> np.ndarray:
    # Python can read Unicode Windows paths; OpenCV path-based load often cannot.
    return np.frombuffer(model_path.read_bytes(), dtype=np.uint8)
