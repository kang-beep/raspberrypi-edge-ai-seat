from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.database.session import get_db
from app.models.reservation import Reservation
from app.models.seat import Seat
from app.models.user import User
from app.schemas.seat import (
    ReservationCreate,
    ReservationPublic,
    SeatCreate,
    SeatPublic,
    SeatUpdate,
)
from app.services import seat_service

router = APIRouter(prefix="/api", tags=["seats"])


@router.get("/seats", response_model=list[SeatPublic])
def get_seats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SeatPublic]:
    seats = seat_service.list_seats(db)
    mine = seat_service.get_active_reservation_seat_ids(db, current_user.id)
    reserved = seat_service.get_active_reservation_seat_ids(db)
    return [
        _to_seat_public(db, seat, seat.id in mine, seat.id in reserved)
        for seat in seats
    ]


@router.post("/seats", response_model=SeatPublic)
def post_seat(
    payload: SeatCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> SeatPublic:
    seat = seat_service.create_seat(db, payload)
    return _to_seat_public(db, seat, False, False)


@router.patch("/seats/{seat_id}", response_model=SeatPublic)
def patch_seat(
    seat_id: int,
    payload: SeatUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> SeatPublic:
    seat = seat_service.update_seat(db, seat_id, payload)
    return _to_seat_public(db, seat, False, False)


@router.post("/seats/{seat_id}/unbind-device", response_model=SeatPublic)
def unbind_seat_device(
    seat_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> SeatPublic:
    seat = seat_service.unbind_device(db, seat_id)
    return _to_seat_public(db, seat, False, False)


@router.get(
    "/seats/{seat_id}/reservations",
    response_model=list[ReservationPublic],
)
def get_seat_reservations(
    seat_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[ReservationPublic]:
    items = seat_service.list_seat_reservations(db, seat_id)
    return [_to_reservation_public(db, item) for item in items]


@router.post("/seats/{seat_id}/reservations", response_model=ReservationPublic)
def post_reservation(
    seat_id: int,
    payload: ReservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReservationPublic:
    reservation = seat_service.reserve_seat(db, seat_id, current_user, payload)
    return _to_reservation_public(db, reservation)


@router.get("/reservations/me", response_model=list[ReservationPublic])
def get_my_reservations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ReservationPublic]:
    items = seat_service.list_my_reservations(db, current_user.id)
    return [_to_reservation_public(db, item) for item in items]


@router.post(
    "/reservations/{reservation_id}/cancel",
    response_model=ReservationPublic,
)
def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReservationPublic:
    reservation = seat_service.cancel_reservation(
        db,
        reservation_id,
        current_user,
    )
    return _to_reservation_public(db, reservation)


def _to_seat_public(
    db: Session,
    seat: Seat,
    reserved_by_me: bool,
    is_reserved: bool,
) -> SeatPublic:
    user_name = None
    if seat.current_user_id is not None:
        user = db.get(User, seat.current_user_id)
        user_name = user.full_name if user else None
    return SeatPublic(
        id=seat.id,
        name=seat.name,
        row=seat.row,
        col=seat.col,
        device_id=seat.device_id,
        active=seat.active,
        status=seat.status,
        current_user_id=seat.current_user_id,
        current_user_name=user_name,
        updated_at=seat.updated_at,
        reserved_by_me=reserved_by_me,
        is_reserved=is_reserved,
    )


def _to_reservation_public(db: Session, item: Reservation) -> ReservationPublic:
    seat = db.get(Seat, item.seat_id)
    user = db.get(User, item.user_id)
    return ReservationPublic(
        id=item.id,
        seat_id=item.seat_id,
        seat_name=seat.name if seat else "",
        user_id=item.user_id,
        user_name=user.full_name if user else None,
        starts_at=item.starts_at,
        ends_at=item.ends_at,
        status=item.status,
        created_at=item.created_at,
    )
