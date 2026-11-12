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
    GALLERY_DIR,
    WINDOW_NAME,
)
from download_model import ensure_sface_model
from gallery import load_gallery
from recognizer import SFaceRecognizer
from visualize import draw_identity
from yunet_bridge import load_yunet_api


def main() -> int:
    sface_model = ensure_sface_model()
    ensure_yunet_model, YuNetDetector = load_yunet_api()
    yunet_model = ensure_yunet_model()

    recognizer = SFaceRecognizer(sface_model)
    gallery = load_gallery(recognizer)
    if not gallery:
        print(f"Put enrolled face images into: {GALLERY_DIR}")
        return 1

    capture = _open_camera()
    if capture is None:
        return 1

    width, height = _frame_size(capture)
    detector = YuNetDetector(yunet_model, (width, height))
    print(f"SFace model: {sface_model}")
    print(f"Gallery size: {len(gallery)}")
    print("SFace webcam demo started. Press 'q' to quit.")

    try:
        _run_loop(capture, detector, recognizer, gallery)
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
    detector: object,
    recognizer: SFaceRecognizer,
    gallery: dict[str, np.ndarray],
) -> None:
    while True:
        ok, frame = capture.read()
        if not ok:
            print("Failed to read frame from webcam")
            break

        detector.set_input_size(frame.shape[1], frame.shape[0])
        faces = detector.detect(frame)
        view = frame.copy()
        for face in faces:
            query = recognizer.embed(frame, face.raw)
            name, score = recognizer.best_match(query, gallery)
            draw_identity(
                view,
                (face.x, face.y, face.width, face.height),
                name,
                score,
            )

        cv2.imshow(WINDOW_NAME, view)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


if __name__ == "__main__":
    sys.exit(main())
