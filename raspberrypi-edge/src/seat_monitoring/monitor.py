from __future__ import annotations

import logging
import time

from config import settings
from mqtt.client import EdgeMqttClient
from sensors.presence import PresenceSensor

logger = logging.getLogger(__name__)


class SeatMonitor:
    def __init__(self, mqtt: EdgeMqttClient, sensor: PresenceSensor) -> None:
        self._mqtt = mqtt
        self._sensor = sensor
        self._last_status = "empty"

    def run_forever(self) -> None:
        interval = max(5, settings.heartbeat_interval_seconds)
        logger.info("Seat monitor started (heartbeat=%ss)", interval)
        while True:
            occupied = self._sensor.read_occupied()
            status = "occupied" if occupied else "empty"
            if status != self._last_status:
                self._mqtt.publish_status(status)
                self._last_status = status
                logger.info("Published status=%s", status)
            self._mqtt.publish_health(ok=True, status=self._last_status)
            time.sleep(interval)
