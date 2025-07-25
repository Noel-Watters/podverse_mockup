import { DateTime } from "luxon";

// Parse a naive ISO string as UTC
export function parseNaiveAsUTC(dt: string) {
  return DateTime.fromISO(dt, { zone: "utc" });
}

// Format for display in local time
export function formatLocal(dt: string, fmt = "M/d/yy HH:mm") {
  return parseNaiveAsUTC(dt).toLocal().toFormat(fmt);
}

// Get duration between two naive datetimes
export function getDuration(start: string, end: string) {
  const startDT = parseNaiveAsUTC(start);
  const endDT = parseNaiveAsUTC(end);
  return endDT.diff(startDT, ["hours", "minutes", "seconds"]).toObject();
}