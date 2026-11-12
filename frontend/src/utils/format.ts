const DATE_TIME_OPTIONS: Intl.DateTimeFormatOptions = {
  month: "short",
  day: "numeric",
  hour: "2-digit",
  minute: "2-digit",
};

export function formatTimestamp(value: string): string {
  return new Intl.DateTimeFormat("ko-KR", DATE_TIME_OPTIONS).format(
    new Date(value),
  );
}
