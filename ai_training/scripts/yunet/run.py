from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from config import (
    CAMERA_INDEX,
    FRAME_HEIGHT,
    FRAME_WIDTH,
    WINDOW_NAME,
)
from crop import save_face_crop
from detector import FaceDetection, YuNetDetector
from download_model import ensure_yunet_model
from visualize import draw_detections


def main() -> int:
    model_path = ensure_yunet_model()
    capture = _open_camera()
    if capture is None:
        return 1

    width, height = _frame_size(capture)
    detector = YuNetDetector(model_path, (width, height))
    print(f"YuNet model: {model_path}")
    print("YuNet webcam demo started. Press 'q' to quit and save one face crop.")

    try:
        last_frame, last_faces = _run_loop(capture, detector)
        if last_frame is not None:
            save_face_crop(last_frame, last_faces)
    finally:
        capture.release()
        cv2.destroyAllWindows()
    return 0


def _open_camera() -> cv2.VideoCapture | None:
    capture = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    if capture.isOpened():
        return capture

    print(f"Failed to open camera index {CAMERA_INDEX}")
    return None


def _frame_size(capture: cv2.VideoCapture) -> tuple[int, int]:
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)) or FRAME_WIDTH
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)) or FRAME_HEIGHT
    return width, height


def _run_loop(
    capture: cv2.VideoCapture,
    detector: YuNetDetector,
) -> tuple[np.ndarray | None, list[FaceDetection]]:
    last_frame: np.ndarray | None = None
    last_faces: list[FaceDetection] = []

    while True:
        ok, frame = capture.read()
        if not ok:
            print("Failed to read frame from webcam")
            break

        detector.set_input_size(frame.shape[1], frame.shape[0])
        faces = detector.detect(frame)
        last_frame = frame
        last_faces = faces
        view = draw_detections(frame, faces)
        cv2.imshow(WINDOW_NAME, view)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    return last_frame, last_faces


if __name__ == "__main__":
    sys.exit(main())
