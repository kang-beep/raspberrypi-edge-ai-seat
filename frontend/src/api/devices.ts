import { apiRequest } from "./client";

export interface DeviceInfo {
  deviceId: string;
  online: boolean;
  inUse: boolean;
  boundSeatId: number | null;
  boundSeatName: string | null;
  lastSeenAt: string;
  selectable: boolean;
}

interface DeviceDto {
  device_id: string;
  online: boolean;
  in_use: boolean;
  bound_seat_id: number | null;
  bound_seat_name: string | null;
  last_seen_at: string;
  selectable: boolean;
}

export async function fetchDevices(): Promise<DeviceInfo[]> {
  const rows = await apiRequest<DeviceDto[]>("/api/devices");
  return rows.map((row) => ({
    deviceId: row.device_id,
    online: row.online,
    inUse: row.in_use,
    boundSeatId: row.bound_seat_id,
    boundSeatName: row.bound_seat_name,
    lastSeenAt: row.last_seen_at,
    selectable: row.selectable,
  }));
}
