import type { ValidationRunResponse } from "../types";
import { StatusBadge } from "./StatusBadge";

type VerdictCardProps = {
  validation: ValidationRunResponse | null;
};

export function VerdictCard({ validation }: VerdictCardProps) {
  if (!validation) {
    return (
      <section className="panel verdict-panel">
        <div>
          <p className="eyebrow">Veredicto sugerido</p>
          <h2>Pendiente</h2>
        </div>
        <StatusBadge value="pendiente" tone="verdict" />
      </section>
    );
  }

  return (
    <section className="panel verdict-panel">
      <div>
        <p className="eyebrow">Veredicto sugerido</p>
        <h2>{validation.verdict.replaceAll("_", " ")}</h2>
      </div>
      <StatusBadge value={validation.verdict} tone="verdict" />
      <dl className="summary-grid">
        <div>
          <dt>OK</dt>
          <dd>{validation.summary.ok ?? 0}</dd>
        </div>
        <div>
          <dt>Advertencias</dt>
          <dd>{validation.summary.advertencias ?? 0}</dd>
        </div>
        <div>
          <dt>Errores</dt>
          <dd>{validation.summary.errores ?? 0}</dd>
        </div>
        <div>
          <dt>Criticas</dt>
          <dd>{validation.summary.criticas ?? 0}</dd>
        </div>
      </dl>
    </section>
  );
}
