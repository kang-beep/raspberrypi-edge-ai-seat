from pathlib import Path

from app.core.config import BACKEND_ROOT

AI_ROOT = BACKEND_ROOT / "ai"
MODELS_DIR = AI_ROOT / "models"
YUNET_MODELS_DIR = MODELS_DIR / "yunet"
SFACE_MODELS_DIR = MODELS_DIR / "sface"
DATA_ROOT = BACKEND_ROOT / "data"
FACES_DIR = DATA_ROOT / "faces"
EMBEDDINGS_DIR = DATA_ROOT / "embeddings"

YUNET_MODEL_NAME = "face_detection_yunet_2023mar.onnx"
SFACE_MODEL_NAME = "face_recognition_sface_2021dec.onnx"
YUNET_MODEL_PATH = YUNET_MODELS_DIR / YUNET_MODEL_NAME
SFACE_MODEL_PATH = SFACE_MODELS_DIR / SFACE_MODEL_NAME

YUNET_MODEL_URL = (
    "https://github.com/opencv/opencv_zoo/raw/main/models/"
    "face_detection_yunet/face_detection_yunet_2023mar.onnx"
)
SFACE_MODEL_URL = (
    "https://github.com/opencv/opencv_zoo/raw/main/models/"
    "face_recognition_sface/face_recognition_sface_2021dec.onnx"
)

# Sibling training models used as local fallback before download.
TRAINING_MODELS_DIR = BACKEND_ROOT.parent / "ai_training" / "models"

SCORE_THRESHOLD = 0.7
NMS_THRESHOLD = 0.3
TOP_K = 5000
CROP_PADDING_RATIO = 0.15

MIN_FACE_WIDTH = 80
MIN_FACE_HEIGHT = 80
MIN_DETECT_SCORE = 0.7
MIN_BLUR_VARIANCE = 60.0
MIN_EMBEDDING_NORM = 1e-3

DEFAULT_INPUT_SIZE = (320, 320)
INFERENCE_TIMEOUT_SECONDS = 30.0
ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/bmp",
}
MAX_UPLOAD_BYTES = 8 * 1024 * 1024
