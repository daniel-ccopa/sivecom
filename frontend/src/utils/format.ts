export function formatDate(value: string): string {
  return new Intl.DateTimeFormat("es-PE", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function formatBytes(bytes: number): string {
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function labelize(value: string | null | undefined): string {
  if (!value) {
    return "-";
  }
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter: string) => letter.toUpperCase());
}

export function maskSensitive(value: string | null | undefined): string {
  if (!value) {
    return "-";
  }
  return value.replace(/\b(\d{2})\d{7}(\d{2})\b/g, "$1*******$2");
}

export function formatMoney(value: string | null | undefined): string {
  if (!value) {
    return "-";
  }
  const parsed = Number(value);
  if (Number.isNaN(parsed)) {
    return value;
  }
  return new Intl.NumberFormat("es-PE", {
    style: "currency",
    currency: "PEN",
  }).format(parsed);
}
