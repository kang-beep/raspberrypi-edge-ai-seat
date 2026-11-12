from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.reservation import Reservation
from app.models.seat import Seat
from app.models.user import User
from app.schemas.seat import ReservationCreate, SeatCreate, SeatUpdate
from app.services.device_service import assert_device_bindable

ACTIVE_RESERVATION_STATUSES = ("reserved", "checked_in")
OCCUPIED_STATUSES = ("occupied", "short_away", "away")
PAST_TOLERANCE = timedelta(minutes=1)


def list_seats(db: Session) -> list[Seat]:
    return list(db.scalars(select(Seat).order_by(Seat.row, Seat.col)).all())


def create_seat(db: Session, payload: SeatCreate) -> Seat:
    row, col = _resolve_position(db, payload.row, payload.col)
    exists = db.scalar(select(Seat).where(Seat.name == payload.name))
    if exists is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Seat name already exists")

    device_id = payload.device_id.strip()
    assert_device_bindable(db, device_id)
    seat = Seat(
        name=payload.name,
        device_id=device_id,
        row=row,
        col=col,
        active=True,
        status="empty",
    )
    db.add(seat)
    db.commit()
    db.refresh(seat)
    return seat


def update_seat(db: Session, seat_id: int, payload: SeatUpdate) -> Seat:
    seat = _get_seat(db, seat_id)
    if payload.name is not None:
        seat.name = payload.name
    if payload.device_id is not None:
        next_device = payload.device_id.strip()
        if next_device:
            assert_device_bindable(db, next_device, current_seat_id=seat.id)
        seat.device_id = next_device
    if payload.active is not None:
        seat.active = payload.active
    if payload.status is not None:
        seat.status = payload.status
    db.add(seat)
    db.commit()
    db.refresh(seat)
    return seat


def unbind_device(db: Session, seat_id: int) -> Seat:
    seat = _get_seat(db, seat_id)
    seat.device_id = ""
    db.add(seat)
    db.commit()
    db.refresh(seat)
    return seat


def reserve_seat(
    db: Session,
    seat_id: int,
    user: User,
    payload: ReservationCreate,
) -> Reservation:
    seat = _get_seat(db, seat_id)
    if not seat.active:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Seat is inactive")
    if not user.face_enrolled:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Face enrollment required",
        )

    starts_at = _as_utc(payload.starts_at)
    ends_at = _as_utc(payload.ends_at)
    now = datetime.now(UTC)
    if starts_at < now - PAST_TOLERANCE:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Reservation start time cannot be in the past",
        )
    if ends_at <= starts_at:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Reservation end time must be after start time",
        )

    if _overlaps_current_occupancy(seat, starts_at, ends_at, now):
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Seat is currently in use during the selected time",
        )
    if _has_reservation_conflict(db, seat_id, starts_at, ends_at):
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Seat reservation overlaps an existing booking",
        )

    reservation = Reservation(
        seat_id=seat.id,
        user_id=user.id,
        starts_at=starts_at,
        ends_at=ends_at,
        status="reserved",
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


def list_my_reservations(db: Session, user_id: int) -> list[Reservation]:
    stmt = (
        select(Reservation)
        .where(Reservation.user_id == user_id)
        .order_by(Reservation.starts_at.desc())
    )
    return list(db.scalars(stmt).all())


def cancel_reservation(
    db: Session,
    reservation_id: int,
    user: User,
) -> Reservation:
    reservation = db.get(Reservation, reservation_id)
    if reservation is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Reservation not found")
    if reservation.user_id != user.id and user.role != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not your reservation")
    if reservation.status not in ACTIVE_RESERVATION_STATUSES:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "이미 취소되었거나 종료된 예약입니다.",
        )
    reservation.status = "cancelled"
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


def list_seat_reservations(db: Session, seat_id: int) -> list[Reservation]:
    _get_seat(db, seat_id)
    now = datetime.now(UTC)
    stmt = (
        select(Reservation)
        .where(
            Reservation.seat_id == seat_id,
            Reservation.status.in_(ACTIVE_RESERVATION_STATUSES),
            Reservation.ends_at >= now,
        )
        .order_by(Reservation.starts_at.asc())
    )
    return list(db.scalars(stmt).all())


def get_active_reservation_seat_ids(
    db: Session,
    user_id: int | None = None,
) -> set[int]:
    now = datetime.now(UTC)
    conditions = [
        Reservation.status.in_(ACTIVE_RESERVATION_STATUSES),
        Reservation.starts_at <= now,
        Reservation.ends_at >= now,
    ]
    if user_id is not None:
        conditions.append(Reservation.user_id == user_id)
    stmt = select(Reservation.seat_id).where(*conditions)
    return set(db.scalars(stmt).all())


def _get_seat(db: Session, seat_id: int) -> Seat:
    seat = db.get(Seat, seat_id)
    if seat is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Seat not found")
    return seat


def _resolve_position(
    db: Session,
    row: int | None,
    col: int | None,
) -> tuple[int, int]:
    if row is not None and col is not None:
        taken = db.scalar(select(Seat).where(Seat.row == row, Seat.col == col))
        if taken is not None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Seat position taken")
        return row, col

    seats = list_seats(db)
    max_row = max((seat.row for seat in seats), default=-1)
    max_col = max((seat.col for seat in seats), default=1)
    cols = max(2, max_col + 1)
    rows = max(1, max_row + 1)
    occupied = {(seat.row, seat.col) for seat in seats}
    for r in range(rows):
        for c in range(cols):
            if (r, c) not in occupied:
                return r, c
    return rows, 0


def _has_reservation_conflict(
    db: Session,
    seat_id: int,
    starts_at: datetime,
    ends_at: datetime,
) -> bool:
    stmt = select(Reservation.id).where(
        Reservation.seat_id == seat_id,
        Reservation.status.in_(ACTIVE_RESERVATION_STATUSES),
        and_(
            Reservation.starts_at < ends_at,
            Reservation.ends_at > starts_at,
        ),
    )
    return db.scalar(stmt) is not None


def _overlaps_current_occupancy(
    seat: Seat,
    starts_at: datetime,
    ends_at: datetime,
    now: datetime,
) -> bool:
    if seat.status not in OCCUPIED_STATUSES:
        return False
    return starts_at <= now < ends_at


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
