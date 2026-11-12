import { useCallback, useEffect, useState } from "react";
import type { FormEvent } from "react";
import { fetchDevices } from "../api/devices";
import type { DeviceInfo } from "../api/devices";
import {
  createSeat,
  fetchSeats,
  unbindSeatDevice,
  updateSeat,
} from "../api/seats";
import { StatusBadge } from "../components/StatusBadge";
import type { Seat } from "../types/domain";
import { buildSeatName } from "../utils/deviceId";
import { formatTimestamp } from "../utils/format";
import { nextSeatPosition, rowLabel } from "../utils/seatLayout";

export function SeatManagePage() {
  const [seats, setSeats] = useState<Seat[]>([]);
  const [devices, setDevices] = useState<DeviceInfo[]>([]);
  const [name, setName] = useState("");
  const [deviceId, setDeviceId] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    const [nextSeats, nextDevices] = await Promise.all([
      fetchSeats(),
      fetchDevices(),
    ]);
    setSeats(nextSeats);
    setDevices(nextDevices);
    const position = nextSeatPosition(nextSeats);
    setName(buildSeatName(position.row, position.col));
    const firstSelectable = nextDevices.find((item) => item.selectable);
    setDeviceId(firstSelectable?.deviceId ?? "");
  }, []);

  useEffect(() => {
    void load().catch((err: unknown) => {
      setError(err instanceof Error ? err.message : "좌석 조회 실패");
    });
  }, [load]);

  async function handleCreate(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    const trimmedName = name.trim();
    const trimmedDevice = deviceId.trim();
    if (!trimmedName || !trimmedDevice) {
      setError("좌석 이름과 장치를 선택하세요.");
      return;
    }
    setError("");
    setBusy(true);
    try {
      await createSeat({
        name: trimmedName,
        device_id: trimmedDevice,
      });
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "좌석 추가 실패");
    } finally {
      setBusy(false);
    }
  }

  async function toggleActive(seat: Seat): Promise<void> {
    setError("");
    try {
      await updateSeat(seat.id, { active: !seat.active });
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "좌석 수정 실패");
    }
  }

  async function handleUnbind(seat: Seat): Promise<void> {
    if (!seat.deviceId) {
      return;
    }
    if (!window.confirm(`${seat.deviceId} 장치 연결을 해제할까요?`)) {
      return;
    }
    setError("");
    try {
      await unbindSeatDevice(seat.id);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "장치 해제 실패");
    }
  }

  return (
    <section>
      <div className="page-header">
        <div>
          <h1>좌석 관리</h1>
          <p>
            온라인 Pi(`raspi-a1` 형식)만 선택해 좌석에 연결합니다. 사용 중인
            장치는 해제 후 다시 연결하세요.
          </p>
        </div>
      </div>

      <form className="panel form-stack" onSubmit={handleCreate}>
        <h2>좌석 추가</h2>
        <label>
          좌석 이름
          <input
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="예: Seat A1"
            required
          />
        </label>
        <label>
          Raspberry Pi 장치
          <select
            value={deviceId}
            onChange={(event) => setDeviceId(event.target.value)}
            required
          >
            <option value="" disabled>
              장치를 선택하세요
            </option>
            {devices.map((device) => (
              <option
                key={device.deviceId}
                value={device.deviceId}
                disabled={!device.selectable}
              >
                {formatDeviceOption(device)}
              </option>
            ))}
          </select>
        </label>
        {devices.length === 0 && (
          <p className="muted">
            등록된 장치가 없습니다. Pi에서 MQTT health가 오는지 확인하세요.
          </p>
        )}
        {error && <p className="field-error">{error}</p>}
        <button className="btn btn-primary" type="submit" disabled={busy}>
          {busy ? "추가 중..." : "추가"}
        </button>
      </form>

      <div className="panel" style={{ marginTop: "1rem" }}>
        <h2>좌석 목록</h2>
        {seats.length === 0 ? (
          <p className="muted">등록된 좌석이 없습니다.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>이름</th>
                  <th>위치</th>
                  <th>상태</th>
                  <th>장치 ID</th>
                  <th>갱신</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {seats.map((seat) => (
                  <tr key={seat.id}>
                    <td>{seat.name}</td>
                    <td>
                      {rowLabel(seat.row)}
                      {seat.col + 1}
                    </td>
                    <td>
                      <StatusBadge
                        tone={seat.active ? seat.status : "inactive"}
                      />
                    </td>
                    <td>{seat.deviceId || "—"}</td>
                    <td>{formatTimestamp(seat.updatedAt)}</td>
                    <td>
                      <div className="button-row">
                        <button
                          className="btn btn-secondary"
                          type="button"
                          onClick={() => void toggleActive(seat)}
                        >
                          {seat.active ? "비활성" : "활성"}
                        </button>
                        {seat.deviceId && (
                          <button
                            className="btn btn-danger"
                            type="button"
                            onClick={() => void handleUnbind(seat)}
                          >
                            장치 해제
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}

function formatDeviceOption(device: DeviceInfo): string {
  if (!device.online) {
    return `${device.deviceId} (오프라인)`;
  }
  if (device.inUse) {
    return `${device.deviceId} (사용 중 · ${device.boundSeatName ?? "좌석"})`;
  }
  return `${device.deviceId} (온라인)`;
}
