import type { Seat } from "../types/domain";

export const LAYOUT_COLUMNS = 2;

export function getLayoutBounds(seats: Seat[]): { rows: number; cols: number } {
  if (seats.length === 0) {
    return { rows: 1, cols: LAYOUT_COLUMNS };
  }

  const maxRow = Math.max(...seats.map((seat) => seat.row));
  const maxCol = Math.max(...seats.map((seat) => seat.col));
  return {
    rows: maxRow + 1,
    cols: Math.max(LAYOUT_COLUMNS, maxCol + 1),
  };
}

export function findSeatAt(
  seats: Seat[],
  row: number,
  col: number,
): Seat | undefined {
  return seats.find((seat) => seat.row === row && seat.col === col);
}

export function nextSeatPosition(seats: Seat[]): { row: number; col: number } {
  const { rows, cols } = getLayoutBounds(seats);

  for (let row = 0; row < rows; row += 1) {
    for (let col = 0; col < cols; col += 1) {
      if (!findSeatAt(seats, row, col)) {
        return { row, col };
      }
    }
  }

  return { row: rows, col: 0 };
}

export function rowLabel(row: number): string {
  return String.fromCharCode(65 + row);
}
