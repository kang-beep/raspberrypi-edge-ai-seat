from __future__ import annotations

import cv2
import numpy as np

from app.ai.config import (
    CROP_PADDING_RATIO,
    MIN_BLUR_VARIANCE,
    MIN_DETECT_SCORE,
    MIN_EMBEDDING_NORM,
    MIN_FACE_HEIGHT,
    MIN_FACE_WIDTH,
)
from app.ai.detector import FaceDetection


class FaceQualityError(ValueError):
    """Raised when uploaded face image fails quality checks."""


def select_best_face(faces: list[FaceDetection]) -> FaceDetection:
    if not faces:
        raise FaceQualityError("얼굴을 찾을 수 없습니다. 정면 사진을 올려주세요.")
    return max(faces, key=lambda face: face.score * face.width * face.height)


def crop_face(frame: np.ndarray, face: FaceDetection) -> np.ndarray:
    height, width = frame.shape[:2]
    pad_x = int(face.width * CROP_PADDING_RATIO)
    pad_y = int(face.height * CROP_PADDING_RATIO)
    x1 = max(0, face.x - pad_x)
    y1 = max(0, face.y - pad_y)
    x2 = min(width, face.x + face.width + pad_x)
    y2 = min(height, face.y + face.height + pad_y)
    crop = frame[y1:y2, x1:x2].copy()
    if crop.size == 0:
        raise FaceQualityError("얼굴 영역을 자를 수 없습니다. 다시 촬영해주세요.")
    return crop


def validate_detection(face: FaceDetection) -> None:
    if face.score < MIN_DETECT_SCORE:
        raise FaceQualityError(
            "얼굴 인식 점수가 너무 낮습니다. 더 선명한 사진을 올려주세요.",
        )
    if face.width < MIN_FACE_WIDTH or face.height < MIN_FACE_HEIGHT:
        raise FaceQualityError(
            "얼굴 영역이 너무 작습니다. 가까이서 촬영해주세요.",
        )


def validate_blur(crop: np.ndarray) -> None:
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    variance = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    if variance < MIN_BLUR_VARIANCE:
        raise FaceQualityError(
            "이미지 화질이 너무 낮습니다. 선명한 사진으로 다시 시도해주세요.",
        )


def validate_embedding(embedding: np.ndarray) -> None:
    if embedding is None or embedding.size == 0:
        raise FaceQualityError(
            "얼굴 특징 추출에 실패했습니다. 다른 사진으로 시도해주세요.",
        )
    if not np.isfinite(embedding).all():
        raise FaceQualityError(
            "얼굴 특징 추출에 실패했습니다. 다른 사진으로 시도해주세요.",
        )
    norm = float(np.linalg.norm(embedding))
    if norm < MIN_EMBEDDING_NORM:
        raise FaceQualityError(
            "얼굴 특징 추출에 실패했습니다. 다른 사진으로 시도해주세요.",
        )
