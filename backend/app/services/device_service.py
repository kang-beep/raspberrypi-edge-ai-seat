from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.device import Device
from app.models.seat import Seat

ONLINE_TIMEOUT = timedelta(seconds=45)


def upsert_health(db: Session, device_id: str) -> Device:
    cleaned = device_id.strip()
    if not cleaned:
        raise ValueError("device_id is required")
    device = db.get(Device, cleaned)
    now = datetime.now(UTC)
    if device is None:
        device = Device(device_id=cleaned, last_seen_at=now)
    else:
        device.last_seen_at = now
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


def list_devices(db: Session) -> list[dict[str, object]]:
    devices = list(db.scalars(select(Device).order_by(Device.device_id)).all())
    seats = list(db.scalars(select(Seat)).all())
    seat_by_device = {
        seat.device_id: seat for seat in seats if seat.device_id.strip()
    }
    now = datetime.now(UTC)
    rows: list[dict[str, object]] = []
    for device in devices:
        online = _is_online(device.last_seen_at, now)
        bound = seat_by_device.get(device.device_id)
        in_use = bound is not None
        rows.append(
            {
                "device_id": device.device_id,
                "online": online,
                "in_use": in_use,
                "bound_seat_id": bound.id if bound else None,
                "bound_seat_name": bound.name if bound else None,
                "last_seen_at": device.last_seen_at,
                "selectable": online and not in_use,
            }
        )
    return rows


def assert_device_bindable(
    db: Session,
    device_id: str,
    *,
    current_seat_id: int | None = None,
) -> None:
    cleaned = device_id.strip()
    if not cleaned:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "장치 ID를 선택하세요.",
        )
    device = db.get(Device, cleaned)
    if device is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "등록되지 않은 장치입니다. Pi health를 확인하세요.",
        )
    if not _is_online(device.last_seen_at, datetime.now(UTC)):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "오프라인 장치는 연결할 수 없습니다.",
        )
    owner = db.scalar(select(Seat).where(Seat.device_id == cleaned))
    if owner is not None and owner.id != current_seat_id:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"장치가 이미 사용 중입니다 ({owner.name}). 먼저 해제하세요.",
        )


def _is_online(last_seen_at: datetime, now: datetime) -> bool:
    seen = last_seen_at
    if seen.tzinfo is None:
        seen = seen.replace(tzinfo=UTC)
    timeout = timedelta(seconds=settings.device_online_timeout_seconds)
    return now - seen <= timeout
