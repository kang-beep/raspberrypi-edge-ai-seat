from __future__ import annotations

import logging
import signal
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import settings
from mqtt import EdgeMqttClient
from seat_monitoring import SeatMonitor
from sensors import PresenceSensor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("smartseat-edge")


def main() -> None:
    mqtt = EdgeMqttClient()
    sensor = PresenceSensor()
    monitor = SeatMonitor(mqtt, sensor)
    stopping = False

    def _shutdown(_signum: int, _frame: object) -> None:
        nonlocal stopping
        if stopping:
            return
        stopping = True
        logger.info("Shutting down edge runtime")
        mqtt.stop()
        raise SystemExit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    logger.info(
        "Starting edge device_id=%s seat=%s",
        settings.device_id,
        settings.seat_name,
    )
    mqtt.start()
    monitor.run_forever()


if __name__ == "__main__":
    main()
