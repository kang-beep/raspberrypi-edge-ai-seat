from pathlib import Path

YUNET_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = YUNET_DIR.parent
AI_TRAINING_DIR = SCRIPTS_DIR.parent
MODELS_DIR = AI_TRAINING_DIR / "models"
CROPS_DIR = YUNET_DIR / "crops"

YUNET_MODEL_NAME = "face_detection_yunet_2023mar.onnx"
YUNET_MODEL_PATH = MODELS_DIR / YUNET_MODEL_NAME
YUNET_MODEL_URL = (
    "https://github.com/opencv/opencv_zoo/raw/main/models/"
    "face_detection_yunet/face_detection_yunet_2023mar.onnx"
)

CAMERA_INDEX = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
SCORE_THRESHOLD = 0.7
NMS_THRESHOLD = 0.3
TOP_K = 5000
CROP_PADDING_RATIO = 0.15
CROP_FILE_NAME = "face_crop.jpg"

WINDOW_NAME = "YuNet Face Detection"
BOX_COLOR = (0, 0, 255)
BOX_THICKNESS = 2
LANDMARK_RADIUS = 3
LANDMARK_COLORS = {
    "right_eye": (255, 0, 0),
    "left_eye": (255, 128, 0),
    "nose": (0, 255, 0),
    "right_mouth": (255, 0, 255),
    "left_mouth": (0, 255, 255),
}
