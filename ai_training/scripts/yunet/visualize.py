from __future__ import annotations

import cv2
import numpy as np

from config import BOX_COLOR, BOX_THICKNESS, LANDMARK_COLORS, LANDMARK_RADIUS
from detector import FaceDetection


def draw_detections(frame: np.ndarray, faces: list[FaceDetection]) -> np.ndarray:
    output = frame.copy()
    for face in faces:
        _draw_box(output, face)
        _draw_landmarks(output, face)
        _draw_score(output, face)
    return output


def _draw_box(frame: np.ndarray, face: FaceDetection) -> None:
    top_left = (face.x, face.y)
    bottom_right = (face.x + face.width, face.y + face.height)
    cv2.rectangle(frame, top_left, bottom_right, BOX_COLOR, BOX_THICKNESS)


def _draw_landmarks(frame: np.ndarray, face: FaceDetection) -> None:
    points = {
        "right_eye": face.right_eye,
        "left_eye": face.left_eye,
        "nose": face.nose,
        "right_mouth": face.right_mouth,
        "left_mouth": face.left_mouth,
    }
    for name, point in points.items():
        color = LANDMARK_COLORS[name]
        cv2.circle(frame, point, LANDMARK_RADIUS, color, -1)


def _draw_score(frame: np.ndarray, face: FaceDetection) -> None:
    label = f"{face.score:.2f}"
    origin = (face.x, max(20, face.y - 8))
    cv2.putText(
        frame,
        label,
        origin,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        BOX_COLOR,
        2,
        cv2.LINE_AA,
    )
