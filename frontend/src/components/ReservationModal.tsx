import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { fetchSeatReservations } from "../api/seats";
import type { Reservation, ReservationRequest, Seat } from "../types/domain";
import { defaultReservationWindow } from "../utils/datetime";
import { formatTimestamp } from "../utils/format";
import { StatusBadge } from "./StatusBadge";

interface ReservationModalProps {
  seat: Seat;
  busy: boolean;
  onClose: () => void;
  onReserve: (seatId: number, request: ReservationRequest) => Promise<void>;
}

export function ReservationModal({
  seat,
  busy,
  onClose,
  onReserve,
}: ReservationModalProps) {
  const defaults = defaultReservationWindow();
  const [date, setDate] = useState(defaults.date);
  const [startTime, setStartTime] = useState(defaults.startTime);
  const [endTime, setEndTime] = useState(defaults.endTime);
  const [bookings, setBookings] = useState<Reservation[]>([]);
  const [localError, setLocalError] = useState("");

  useEffect(() => {
    const next = defaultReservationWindow();
    setDate(next.date);
    setStartTime(next.startTime);
    setEndTime(next.endTime);
    setLocalError("");
    void fetchSeatReservations(seat.id)
      .then(setBookings)
      .catch(() => setBookings([]));
  }, [seat.id]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    const startsAt = new Date(`${date}T${startTime}:00`);
    const endsAt = new Date(`${date}T${endTime}:00`);
    if (Number.isNaN(startsAt.getTime()) || Number.isNaN(endsAt.getTime())) {
      setLocalError("날짜와 시간을 확인해 주세요.");
      return;
    }
    if (endsAt <= startsAt) {
      setLocalError("종료 시간은 시작 시간보다 뒤여야 합니다.");
      return;
    }

    setLocalError("");
    try {
      await onReserve(seat.id, {
        startsAt: startsAt.toISOString(),
        endsAt: endsAt.toISOString(),
      });
      onClose();
    } catch {
      // Parent surfaces API error; keep modal open.
    }
  }

  return (
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <div
        className="modal-card panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="reservation-modal-title"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="modal-header">
          <div>
            <h2 id="reservation-modal-title">{seat.name} 예약</h2>
            <p className="muted">날짜와 이용 시간을 입력하세요.</p>
          </div>
          <StatusBadge tone={seat.active ? seat.status : "inactive"} />
        </div>

        <div className="booking-list">
          <h3 className="detail-subtitle">기존 예약</h3>
          {bookings.length === 0 ? (
            <p className="muted">예정된 예약이 없습니다.</p>
          ) : (
            bookings.map((item) => (
              <div className="booking-item" key={item.id}>
                <strong>{item.userName ?? `user#${item.userId}`}</strong>
                <span>
                  {formatTimestamp(item.startsAt)} ~{" "}
                  {formatTimestamp(item.endsAt)}
                </span>
              </div>
            ))
          )}
        </div>

        <form className="form-stack" onSubmit={(event) => void handleSubmit(event)}>
          <label>
            날짜
            <input
              type="date"
              value={date}
              onChange={(event) => setDate(event.target.value)}
              required
            />
          </label>
          <label>
            시작 시간
            <input
              type="time"
              value={startTime}
              onChange={(event) => setStartTime(event.target.value)}
              required
            />
          </label>
          <label>
            종료 시간
            <input
              type="time"
              value={endTime}
              onChange={(event) => setEndTime(event.target.value)}
              required
            />
          </label>
          {localError && <p className="field-error">{localError}</p>}
          <div className="button-row">
            <button className="btn btn-primary" type="submit" disabled={busy}>
              {busy ? "예약 중..." : "예약하기"}
            </button>
            <button
              className="btn btn-secondary"
              type="button"
              onClick={onClose}
              disabled={busy}
            >
              취소
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
