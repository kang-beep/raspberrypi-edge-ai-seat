/** Seat occupancy lifecycle */
export type SeatStatus =
  | "occupied"
  | "short_away"
  | "away"
  | "empty";

export type EnrollmentPhase =
  | "idle"
  | "waiting_capture"
  | "capturing"
  | "success"
  | "failed";

export interface Seat {
  id: number;
  name: string;
  status: SeatStatus;
  userName: string | null;
  updatedAt: string;
  active: boolean;
  row: number;
  col: number;
  deviceId: string;
  reservedByMe?: boolean;
  isReserved?: boolean;
}

export interface Reservation {
  id: number;
  seatId: number;
  seatName: string;
  userId: number;
  userName?: string | null;
  startsAt: string;
  endsAt: string;
  status: string;
  createdAt: string;
}

export interface ReservationRequest {
  startsAt: string;
  endsAt: string;
}

export interface RegisteredUser {
  id: string;
  name: string;
  enrolledAt: string;
  status: "ready" | "pending" | "failed";
}

export interface AdminSettings {
  shortAwayGraceMinutes: number;
  awayGraceMinutes: number;
}

export const DEFAULT_ADMIN_SETTINGS: AdminSettings = {
  shortAwayGraceMinutes: 5,
  awayGraceMinutes: 15,
};

export const SEAT_STATUS_LABELS: Record<SeatStatus, string> = {
  occupied: "이용 중",
  short_away: "잠시 자리비움",
  away: "자리비움",
  empty: "비어 있음",
};
