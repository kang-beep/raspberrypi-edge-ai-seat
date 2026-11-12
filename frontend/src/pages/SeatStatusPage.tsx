import { useCallback, useEffect, useState } from "react";
import { fetchSeats } from "../api/seats";
import { SeatFloorPlan } from "../components/SeatFloorPlan";
import type { Seat } from "../types/domain";

export function SeatStatusPage() {
  const [seats, setSeats] = useState<Seat[]>([]);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    try {
      setSeats(await fetchSeats());
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "좌석 조회 실패");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <section>
      <div className="page-header">
        <div>
          <h1>좌석 현황</h1>
          <p>실시간 점유 상태를 배치도로 확인합니다.</p>
        </div>
      </div>
      {error && <p className="field-error">{error}</p>}
      <SeatFloorPlan seats={seats} />
    </section>
  );
}
