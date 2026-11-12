import { useCallback, useEffect, useState } from "react";
import {
  cancelReservation,
  fetchMyReservations,
  fetchSeats,
  reserveSeat,
} from "../api/seats";
import { useAuth } from "../auth/AuthContext";
import { SeatFloorPlan } from "../components/SeatFloorPlan";
import { useToast } from "../components/Toast";
import type { Reservation, ReservationRequest, Seat } from "../types/domain";
import { formatTimestamp } from "../utils/format";

export function SeatReservePage() {
  const { user } = useAuth();
  const { showToast } = useToast();
  const [seats, setSeats] = useState<Seat[]>([]);
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [busySeatId, setBusySeatId] = useState<number | null>(null);
  const [cancellingReservationId, setCancellingReservationId] = useState<
    number | null
  >(null);

  const load = useCallback(async () => {
    const [nextSeats, nextReservations] = await Promise.all([
      fetchSeats(),
      fetchMyReservations(),
    ]);
    setSeats(nextSeats);
    setReservations(nextReservations);
  }, []);

  useEffect(() => {
    void load().catch((err: unknown) => {
      showToast(err instanceof Error ? err.message : "좌석 조회 실패", {
        tone: "error",
      });
    });
  }, [load, showToast]);

  function handleReserveBlocked(): void {
    showToast("얼굴 등록 후 예약할 수 있습니다. 먼저 등록해 주세요.", {
      tone: "info",
      action: { label: "얼굴 등록 바로가기", to: "/profile#face" },
      durationMs: 7000,
    });
  }

  async function handleReserve(
    seatId: number,
    request: ReservationRequest,
  ): Promise<void> {
    const seat = seats.find((item) => item.id === seatId);
    if (!seat) {
      return;
    }

    setBusySeatId(seatId);
    try {
      const reservation = await reserveSeat(
        seatId,
        request.startsAt,
        request.endsAt,
      );
      showToast(
        `${reservation.seatName} 예약 완료: ${formatTimestamp(reservation.startsAt)} ~ ${formatTimestamp(reservation.endsAt)}`,
        { tone: "success" },
      );
      await load();
    } catch (err) {
      showToast(err instanceof Error ? err.message : "예약 실패", {
        tone: "error",
      });
      throw err;
    } finally {
      setBusySeatId(null);
    }
  }

  async function handleCancelReservation(reservationId: number): Promise<void> {
    if (!window.confirm("이 예약을 취소할까요?")) {
      return;
    }
    setCancellingReservationId(reservationId);
    try {
      await cancelReservation(reservationId);
      showToast("예약이 취소되었습니다.", { tone: "success" });
      await load();
    } catch (err) {
      showToast(err instanceof Error ? err.message : "예약 취소 실패", {
        tone: "error",
      });
    } finally {
      setCancellingReservationId(null);
    }
  }

  return (
    <section>
      <div className="page-header">
        <div>
          <h1>좌석 예약</h1>
          <p>좌석을 클릭하면 예약 모달이 열립니다. 상세에는 내 예약만 표시됩니다.</p>
        </div>
      </div>

      <SeatFloorPlan
        seats={seats}
        myReservations={reservations}
        reservable
        canReserve={Boolean(user?.face_enrolled)}
        onReserveBlocked={handleReserveBlocked}
        onReserve={handleReserve}
        onCancelReservation={handleCancelReservation}
        busySeatId={busySeatId}
        cancellingReservationId={cancellingReservationId}
      />
    </section>
  );
}
