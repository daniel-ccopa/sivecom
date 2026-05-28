import type { ValidationItem } from "../types";
import { StatusBadge } from "./StatusBadge";

type AlertsTableProps = {
  alerts: ValidationItem[];
};

export function AlertsTable({ alerts }: AlertsTableProps) {
  return (
    <section className="panel">
      <div className="section-header">
        <h2>Alertas</h2>
        <span className="count-pill">{alerts.length}</span>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Tipo</th>
              <th>Severidad</th>
              <th>Mensaje</th>
              <th>Evidencia</th>
            </tr>
          </thead>
          <tbody>
            {alerts.map((item) => (
              <tr key={item.rule_id}>
                <td>{item.tipo.replaceAll("_", " ")}</td>
                <td>
                  <StatusBadge value={item.severidad} tone="severity" />
                </td>
                <td>{item.mensaje}</td>
                <td>
                  {item.evidencia.slice(0, 2).map((evidence, index) => (
                    <p key={`${item.rule_id}-${index}`} className="evidence-line">
                      Pag. {evidence.page ?? "-"}: {evidence.text}
                    </p>
                  ))}
                </td>
              </tr>
            ))}
            {alerts.length === 0 && (
              <tr>
                <td colSpan={4}>No se registraron alertas.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
