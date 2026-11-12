from __future__ import annotations

import asyncio
import threading
from collections.abc import Callable
from concurrent.futures import Future
from dataclasses import dataclass
from queue import Empty, Queue
from typing import Any, Generic, TypeVar

from app.ai.config import INFERENCE_TIMEOUT_SECONDS

T = TypeVar("T")


@dataclass
class _QueuedJob(Generic[T]):
    run: Callable[[], T]
    future: Future[T]


class InferenceQueue:
    """Single-worker queue so YuNet/SFace handle one request at a time."""

    def __init__(self) -> None:
        self._jobs: Queue[Any] = Queue()
        self._thread: threading.Thread | None = None
        self._started = False

    def start(self) -> None:
        if self._started:
            return
        self._started = True
        self._thread = threading.Thread(
            target=self._worker_loop,
            name="face-inference-queue",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        if not self._started:
            return
        self._jobs.put(None)
        if self._thread is not None:
            self._thread.join(timeout=5)
        self._started = False

    def submit(self, run: Callable[[], T]) -> Future[T]:
        if not self._started:
            raise RuntimeError("Inference queue is not running")
        future: Future[T] = Future()
        self._jobs.put(_QueuedJob(run=run, future=future))
        return future

    async def submit_async(self, run: Callable[[], T]) -> T:
        future = self.submit(run)
        return await asyncio.wait_for(
            asyncio.wrap_future(future),
            timeout=INFERENCE_TIMEOUT_SECONDS,
        )

    def _worker_loop(self) -> None:
        while True:
            try:
                job = self._jobs.get(timeout=0.5)
            except Empty:
                continue
            if job is None:
                return
            if not job.future.set_running_or_notify_cancel():
                continue
            try:
                job.future.set_result(job.run())
            except Exception as exc:  # noqa: BLE001 - forward to caller
                job.future.set_exception(exc)
