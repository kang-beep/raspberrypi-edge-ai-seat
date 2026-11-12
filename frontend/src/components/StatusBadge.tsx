import type { EnrollmentPhase, SeatStatus } from "../types/domain";
import { SEAT_STATUS_LABELS } from "../types/domain";

type BadgeTone =
  | SeatStatus
  | "ready"
  | "pending"
  | "failed"
  | "inactive"
  | "unenrolled";

const LABELS: Record<BadgeTone, string> = {
  ...SEAT_STATUS_LABELS,
  ready: "등록 완료",
  pending: "등록 중",
  failed: "등록 실패",
  inactive: "비활성",
  unenrolled: "미등록",
};

interface StatusBadgeProps {
  tone: BadgeTone;
}

export function StatusBadge({ tone }: StatusBadgeProps) {
  return <span className={`status-badge ${tone}`}>{LABELS[tone]}</span>;
}

export function enrollmentTone(
  phase: EnrollmentPhase,
): "ready" | "pending" | "failed" {
  if (phase === "success") {
    return "ready";
  }
  if (phase === "failed") {
    return "failed";
  }
  return "pending";
}
