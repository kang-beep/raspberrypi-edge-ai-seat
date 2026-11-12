from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import select

from app.database.session import SessionLocal
from app.models.seat import Seat
from app.services.device_service import upsert_health

logger = logging.getLogger(__name__)
ALLOWED_STATUSES = {"occupied", "short_away", "away", "empty"}


def handle_edge_message(topic: str, payload: dict[str, Any]) -> None:
    parts = topic.split("/")
    if len(parts) < 4:
        return
    kind = parts[-1]
    if kind == "health":
        _apply_health(topic, payload)
        return
    if kind == "events":
        logger.info("Edge event: %s", payload)
        return
    if kind == "status":
        _apply_status(payload)


def _apply_health(topic: str, payload: dict[str, Any]) -> None:
    device_id = str(payload.get("device_id", "")).strip()
    if not device_id and len(topic.split("/")) >= 4:
        device_id = topic.split("/")[2]
    if not device_id:
        logger.warning("Health without device_id: %s", payload)
        return
    db = SessionLocal()
    try:
        upsert_health(db, device_id)
        logger.info("Device health upserted: %s", device_id)
    except Exception:  # noqa: BLE001
        logger.exception("Failed to upsert device health")
    finally:
        db.close()


def _apply_status(payload: dict[str, Any]) -> None:
    device_id = str(payload.get("device_id", "")).strip()
    status = str(payload.get("status", "")).strip()
    if not device_id or status not in ALLOWED_STATUSES:
        logger.warning("Ignored invalid status payload: %s", payload)
        return

    db = SessionLocal()
    try:
        upsert_health(db, device_id)
        seat = db.scalar(select(Seat).where(Seat.device_id == device_id))
        if seat is None:
            logger.warning("No seat mapped to device_id=%s", device_id)
            return
        if seat.status == status:
            return
        seat.status = status
        db.add(seat)
        db.commit()
        logger.info("Seat %s status -> %s", seat.name, status)
    finally:
        db.close()
