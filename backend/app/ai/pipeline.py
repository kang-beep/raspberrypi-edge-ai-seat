from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from app.ai.detector import YuNetDetector
from app.ai.quality import (
    FaceQualityError,
    crop_face,
    select_best_face,
    validate_blur,
    validate_detection,
    validate_embedding,
)
from app.ai.recognizer import SFaceRecognizer


@dataclass(frozen=True)
class FaceEnrollResult:
    crop_bgr: np.ndarray
    embedding: np.ndarray


class FaceEnrollmentPipeline:
    def __init__(
        self,
        detector: YuNetDetector,
        recognizer: SFaceRecognizer,
    ) -> None:
        self._detector = detector
        self._recognizer = recognizer

    def process(self, image_bytes: bytes) -> FaceEnrollResult:
        frame = _decode_image(image_bytes)
        self._detector.set_input_size(frame.shape[1], frame.shape[0])
        faces = self._detector.detect(frame)
        face = select_best_face(faces)
        validate_detection(face)
        crop = crop_face(frame, face)
        validate_blur(crop)
        try:
            embedding = self._recognizer.embed(frame, face.raw)
        except Exception as exc:  # noqa: BLE001 - OpenCV may raise various errors
            raise FaceQualityError(
                "얼굴 특징 추출에 실패했습니다. 다른 사진으로 시도해주세요.",
            ) from exc
        validate_embedding(embedding)
        return FaceEnrollResult(crop_bgr=crop, embedding=embedding)


def _decode_image(image_bytes: bytes) -> np.ndarray:
    if not image_bytes:
        raise FaceQualityError("이미지 파일이 비어 있습니다.")
    array = np.frombuffer(image_bytes, dtype=np.uint8)
    frame = cv2.imdecode(array, cv2.IMREAD_COLOR)
    if frame is None:
        raise FaceQualityError("이미지 파일을 읽을 수 없습니다.")
    return frame
