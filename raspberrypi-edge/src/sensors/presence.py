from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class PresenceSensor:
    """Ultrasonic presence sensor placeholder.

    Replace `read_occupied` with real GPIO distance sampling later.
    """

    def __init__(self) -> None:
        self._occupied = False

    def read_occupied(self) -> bool:
        return self._occupied

    def set_debug_occupied(self, occupied: bool) -> None:
        self._occupied = occupied
        logger.info("Debug presence -> occupied=%s", occupied)
