import { apiRequest } from "./client";
import type { Reservation, Seat, SeatStatus } from "../types/domain";

interface SeatDto {
  id: number;
  name: string;
  row: number;
  col: number;
  device_id: string;
  active: boolean;
  status: SeatStatus;
  current_user_name: string | null;
  updated_at: string;
  reserved_by_me: boolean;
  is_reserved: boolean;
}

interface ReservationDto {
  id: number;
  seat_id: number;
  seat_name: string;
  user_id: number;
  user_name: string | null;
  starts_at: string;
  ends_at: string;
  status: string;
  created_at: string;
}

export async function fetchSeats(): Promise<Seat[]> {
  const rows = await apiRequest<SeatDto[]>("/api/seats");
  return rows.map(_mapSeat);
}

export async function createSeat(payload: {
  name: string;
  device_id: string;
}): Promise<Seat> {
  const row = await apiRequest<SeatDto>("/api/seats", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  return _mapSeat(row);
}

export async function updateSeat(
  seatId: number,
  payload: { active?: boolean; name?: string; device_id?: string },
): Promise<Seat> {
  const row = await apiRequest<SeatDto>(`/api/seats/${seatId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
  return _mapSeat(row);
}

export async function unbindSeatDevice(seatId: number): Promise<Seat> {
  const row = await apiRequest<SeatDto>(`/api/seats/${seatId}/unbind-device`, {
    method: "POST",
  });
  return _mapSeat(row);
}

export async function reserveSeat(
  seatId: number,
  startsAt: string,
  endsAt: string,
): Promise<Reservation> {
  const row = await apiRequest<ReservationDto>(
    `/api/seats/${seatId}/reservations`,
    {
      method: "POST",
      body: JSON.stringify({
        starts_at: startsAt,
        ends_at: endsAt,
      }),
    },
  );
  return _mapReservation(row);
}

export async function fetchSeatReservations(
  seatId: number,
): Promise<Reservation[]> {
  const rows = await apiRequest<ReservationDto[]>(
    `/api/seats/${seatId}/reservations`,
  );
  return rows.map(_mapReservation);
}

export async function fetchMyReservations(): Promise<Reservation[]> {
  const rows = await apiRequest<ReservationDto[]>("/api/reservations/me");
  return rows.map(_mapReservation);
}

export async function cancelReservation(
  reservationId: number,
): Promise<Reservation> {
  const row = await apiRequest<ReservationDto>(
    `/api/reservations/${reservationId}/cancel`,
    { method: "POST" },
  );
  return _mapReservation(row);
}

function _mapSeat(row: SeatDto): Seat {
  return {
    id: row.id,
    name: row.name,
    status: row.status,
    userName: row.current_user_name,
    updatedAt: row.updated_at,
    active: row.active,
    row: row.row,
    col: row.col,
    deviceId: row.device_id,
    reservedByMe: row.reserved_by_me,
    isReserved: row.is_reserved,
  };
}

function _mapReservation(row: ReservationDto): Reservation {
  return {
    id: row.id,
    seatId: row.seat_id,
    seatName: row.seat_name,
    userId: row.user_id,
    userName: row.user_name,
    startsAt: row.starts_at,
    endsAt: row.ends_at,
    status: row.status,
    createdAt: row.created_at,
  };
}
