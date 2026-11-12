import { rowLabel } from "./seatLayout";

export function buildSeatName(row: number, col: number): string {
  return `Seat ${rowLabel(row)}${col + 1}`;
}

export function buildRaspiDeviceId(index: number): string {
  return `raspi-a${index}`;
}
