import { useMemo, useState } from "react";
import type {
  Reservation,
  ReservationRequest,
  Seat,
  SeatStatus,
} from "../types/domain";
import { formatTimestamp } from "../utils/format";
import {
  findSeatAt,
  getLayoutBounds,
  rowLabel,
} from "../utils/seatLayout";
import { ReservationModal } from "./ReservationModal";
import { SeatStation } from "./SeatStation";

interface SeatFloorPlanProps {
  seats: Seat[];
  myReservations?: Reservation[];
  reservable?: boolean;
  canReserve?: boolean;
  onReserveBlocked?: () => void;
  onReserve?: (
    seatId: number,
    request: ReservationRequest,
  ) => Promise<void>;
  onCancelReservation?: (reservationId: number) => Promise<void>;
  busySeatId?: number | null;
  cancellingReservationId?: number | null;
}

export function SeatFloorPlan({
  seats,
  myReservations = [],
  reservable = false,
  canReserve = true,
  onReserveBlocked,
  onReserve,
  onCancelReservation,
  busySeatId = null,
  cancellingReservationId = null,
}: SeatFloorPlanProps) {
  const activeSeats = useMemo(
    () => seats.filter((seat) => seat.active),
    [seats],
  );
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [modalSeatId, setModalSeatId] = useState<number | null>(null);
  const { rows, cols } = useMemo(() => getLayoutBounds(seats), [seats]);
  const selectedSeat =
    seats.find((seat) => seat.id === selectedId) ?? activeSeats[0] ?? null;
  const modalSeat = seats.find((seat) => seat.id === modalSeatId) ?? null;
  const mySeatReservations = selectedSeat
    ? myReservations.filter((item) => item.seatId === selectedSeat.id)
    : [];
  const summary = useMemo(() => buildSeatSummary(seats), [seats]);

  function handleSelect(seatId: number): void {
    setSelectedId(seatId);
    if (!reservable || !onReserve) {
      return;
    }
    if (!canReserve) {
      onReserveBlocked?.();
      return;
    }
    setModalSeatId(seatId);
  }

  if (seats.length === 0) {
    return (
      <div className="panel empty-state">
        <h2>배치할 좌석이 없습니다</h2>
        <p>관리자가 좌석을 추가하면 여기에 표시됩니다.</p>
      </div>
    );
  }

  return (
    <>
      <div className="floor-plan-layout">
        <div className="floor-plan-panel">
          <div className="floor-plan-toolbar">
            <h2>좌석 배치도</h2>
          </div>

          <div className="floor-stage">
            <div className="floor-window">창가</div>
            <div
              className="floor-grid"
              style={{
                gridTemplateColumns: `auto repeat(${cols}, minmax(120px, 1fr))`,
              }}
            >
              {Array.from({ length: rows }, (_, row) => (
                <FloorRow
                  key={`row-${row}`}
                  row={row}
                  cols={cols}
                  seats={seats}
                  selectedId={selectedSeat?.id ?? null}
                  onSelect={handleSelect}
                />
              ))}
            </div>
            <div className="floor-aisle">중앙 통로</div>
            <div className="floor-entrance">출입구</div>
          </div>
        </div>

        <aside className="floor-detail">
          <div className="panel floor-detail-card">
            <h2>현황 요약</h2>
            <div className="summary-grid">
              <div className="summary-item">
                <span>전체 활성</span>
                <strong>{summary.totalActive}</strong>
              </div>
              <div className="summary-item">
                <span>비어 있음</span>
                <strong>{summary.empty}</strong>
              </div>
              <div className="summary-item">
                <span>이용 중</span>
                <strong>{summary.occupied}</strong>
              </div>
              <div className="summary-item">
                <span>잠시 자리비움</span>
                <strong>{summary.shortAway}</strong>
              </div>
              <div className="summary-item">
                <span>자리비움</span>
                <strong>{summary.away}</strong>
              </div>
              <div className="summary-item">
                <span>지금 예약됨</span>
                <strong>{summary.reservedNow}</strong>
              </div>
            </div>
          </div>

          {reservable && (
            <div className="panel floor-detail-card">
              <h2>내 예약</h2>
              {selectedSeat ? (
                <MyReservationList
                  seatName={selectedSeat.name}
                  reservations={mySeatReservations}
                  onCancel={onCancelReservation}
                  cancellingReservationId={cancellingReservationId}
                />
              ) : (
                <p className="muted">좌석을 선택하세요.</p>
              )}
            </div>
          )}
        </aside>
      </div>

      {modalSeat && onReserve && (
        <ReservationModal
          seat={modalSeat}
          busy={busySeatId === modalSeat.id}
          onClose={() => setModalSeatId(null)}
          onReserve={onReserve}
        />
      )}
    </>
  );
}

interface FloorRowProps {
  row: number;
  cols: number;
  seats: Seat[];
  selectedId: number | null;
  onSelect: (seatId: number) => void;
}

function FloorRow({ row, cols, seats, selectedId, onSelect }: FloorRowProps) {
  return (
    <>
      <div className="floor-row-label">{rowLabel(row)}</div>
      {Array.from({ length: cols }, (_, col) => {
        const seat = findSeatAt(seats, row, col);
        if (!seat) {
          return (
            <div key={`empty-${row}-${col}`} className="seat-slot empty-slot" />
          );
        }
        return (
          <div key={seat.id} className="seat-slot">
            <SeatStation
              seat={seat}
              selected={selectedId === seat.id}
              onSelect={onSelect}
            />
          </div>
        );
      })}
    </>
  );
}

function buildSeatSummary(seats: Seat[]): {
  totalActive: number;
  empty: number;
  occupied: number;
  shortAway: number;
  away: number;
  reservedNow: number;
} {
  const active = seats.filter((seat) => seat.active);
  const count = (status: SeatStatus) =>
    active.filter((seat) => seat.status === status).length;
  return {
    totalActive: active.length,
    empty: count("empty"),
    occupied: count("occupied"),
    shortAway: count("short_away"),
    away: count("away"),
    reservedNow: active.filter((seat) => seat.isReserved).length,
  };
}

const CANCELABLE_STATUSES = new Set(["reserved", "checked_in"]);

function MyReservationList({
  seatName,
  reservations,
  onCancel,
  cancellingReservationId,
}: {
  seatName: string;
  reservations: Reservation[];
  onCancel?: (reservationId: number) => Promise<void>;
  cancellingReservationId?: number | null;
}) {
  if (reservations.length === 0) {
    return <p className="muted">{seatName}에 대한 내 예약이 없습니다.</p>;
  }

  return (
    <div className="booking-list">
      {reservations.map((item) => {
        const canCancel =
          Boolean(onCancel) && CANCELABLE_STATUSES.has(item.status);
        return (
          <div className="booking-item" key={item.id}>
            <strong>{seatName}</strong>
            <span>
              {formatTimestamp(item.startsAt)} ~ {formatTimestamp(item.endsAt)}{" "}
              · {item.status}
            </span>
            {canCancel && (
              <button
                className="btn btn-danger booking-cancel"
                type="button"
                disabled={cancellingReservationId === item.id}
                onClick={() => void onCancel?.(item.id)}
              >
                {cancellingReservationId === item.id ? "취소 중..." : "예약 취소"}
              </button>
            )}
          </div>
        );
      })}
    </div>
  );
}
