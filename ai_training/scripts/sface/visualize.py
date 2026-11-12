from __future__ import annotations

import cv2
import numpy as np

from config import BOX_COLOR, BOX_THICKNESS, TEXT_COLOR, UNKNOWN_COLOR


def draw_identity(
    frame: np.ndarray,
    box: tuple[int, int, int, int],
    name: str,
    score: float,
) -> None:
    x, y, width, height = box
    color = TEXT_COLOR if name != "Unknown" else UNKNOWN_COLOR
    cv2.rectangle(frame, (x, y), (x + width, y + height), BOX_COLOR, BOX_THICKNESS)
    label = f"{name} ({score:.2f})"
    origin = (x, max(24, y - 10))
    cv2.putText(
        frame,
        label,
        origin,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        color,
        2,
        cv2.LINE_AA,
    )
