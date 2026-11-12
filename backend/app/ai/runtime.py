from __future__ import annotations

from app.ai.config import DEFAULT_INPUT_SIZE
from app.ai.detector import YuNetDetector
from app.ai.models import ensure_models
from app.ai.pipeline import FaceEnrollmentPipeline, FaceEnrollResult
from app.ai.queue import InferenceQueue
from app.ai.recognizer import SFaceRecognizer


class FaceAiRuntime:
    def __init__(self) -> None:
        self._queue = InferenceQueue()
        self._pipeline: FaceEnrollmentPipeline | None = None

    @property
    def ready(self) -> bool:
        return self._pipeline is not None

    def start(self) -> None:
        yunet_path, sface_path = ensure_models()
        detector = YuNetDetector(yunet_path, DEFAULT_INPUT_SIZE)
        recognizer = SFaceRecognizer(sface_path)
        self._pipeline = FaceEnrollmentPipeline(detector, recognizer)
        self._queue.start()

    def stop(self) -> None:
        self._queue.stop()
        self._pipeline = None

    async def enroll(self, image_bytes: bytes) -> FaceEnrollResult:
        pipeline = self._pipeline
        if pipeline is None:
            raise RuntimeError("Face AI runtime is not ready")
        return await self._queue.submit_async(lambda: pipeline.process(image_bytes))


face_ai_runtime = FaceAiRuntime()
