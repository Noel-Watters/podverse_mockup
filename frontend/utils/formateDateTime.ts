// frontend/utils/formatDateTime.ts
export function formatDateTime(dateStr: string): string {
  const dateObj = new Date(dateStr);
  const date = dateObj.toLocaleDateString();
  let hours = dateObj.getHours();
  const minutes = dateObj.getMinutes();
  const ampm = hours >= 12 ? "pm" : "am";
  hours = hours % 12;
  if (hours === 0) hours = 12;
  const minStr = minutes < 10 ? `0${minutes}` : `${minutes}`;
  const time = `${hours}:${minStr} ${ampm}`;
  return `${date} ${time}`;
}