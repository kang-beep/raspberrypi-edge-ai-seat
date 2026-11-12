from pathlib import Path

SFACE_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = SFACE_DIR.parent
AI_TRAINING_DIR = SCRIPTS_DIR.parent
YUNET_DIR = SCRIPTS_DIR / "yunet"
MODELS_DIR = AI_TRAINING_DIR / "models"
GALLERY_DIR = SFACE_DIR / "gallery"

SFACE_MODEL_NAME = "face_recognition_sface_2021dec.onnx"
SFACE_MODEL_PATH = MODELS_DIR / SFACE_MODEL_NAME
SFACE_MODEL_URL = (
    "https://github.com/opencv/opencv_zoo/raw/main/models/"
    "face_recognition_sface/face_recognition_sface_2021dec.onnx"
)

YUNET_MODEL_NAME = "face_detection_yunet_2023mar.onnx"
YUNET_MODEL_PATH = MODELS_DIR / YUNET_MODEL_NAME

CAMERA_INDEX = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
# OpenCV SFace cosine threshold reference value.
COSINE_THRESHOLD = 0.363
GALLERY_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

WINDOW_NAME = "SFace Recognition"
BOX_COLOR = (0, 0, 255)
BOX_THICKNESS = 2
TEXT_COLOR = (0, 255, 0)
UNKNOWN_COLOR = (0, 165, 255)
