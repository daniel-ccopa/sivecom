import { labelize } from "../utils/format";

type StatusBadgeProps = {
  value: string | null | undefined;
  tone?: "status" | "verdict" | "severity" | "result";
};

export function StatusBadge({ value, tone = "status" }: StatusBadgeProps) {
  const normalized = value ?? "sin_estado";
  return (
    <span className={`badge badge-${tone} badge-${normalized}`}>
      {labelize(normalized)}
    </span>
  );
}
