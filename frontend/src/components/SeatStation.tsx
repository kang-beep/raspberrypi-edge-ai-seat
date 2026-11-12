import type { Seat } from "../types/domain";
import { SEAT_STATUS_LABELS } from "../types/domain";

interface SeatStationProps {
  seat: Seat;
  selected: boolean;
  onSelect: (seatId: number) => void;
}

export function SeatStation({ seat, selected, onSelect }: SeatStationProps) {
  const className = [
    "seat-station",
    seat.active ? seat.status : "inactive",
    selected ? "selected" : "",
    seat.reservedByMe ? "mine" : "",
  ]
    .filter(Boolean)
    .join(" ");

  const subtitle = !seat.active
    ? "비활성"
    : seat.reservedByMe
      ? "내 예약"
      : seat.isReserved
        ? "예약됨"
        : seat.status === "occupied" ||
            seat.status === "short_away" ||
            seat.status === "away"
          ? seat.userName ?? "이용자"
          : SEAT_STATUS_LABELS.empty;

  return (
    <button
      type="button"
      className={className}
      onClick={() => onSelect(seat.id)}
      aria-pressed={selected}
      aria-label={`${seat.name} ${seat.active ? seat.status : "inactive"}`}
    >
      <span className="seat-desk" />
      <span className="seat-chair" />
      <span className="seat-station-name">{seat.name}</span>
      <span className="seat-station-user">{subtitle}</span>
    </button>
  );
}
