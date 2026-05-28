import type { ExpedienteListItem } from "../types";
import { formatDate, formatMoney, maskSensitive } from "../utils/format";
import { StatusBadge } from "../components/StatusBadge";

type ExpedientesListProps = {
  expedientes: ExpedienteListItem[];
  selectedId: number | null;
  onSelect: (expediente: ExpedienteListItem) => void;
};

export function ExpedientesList({
  expedientes,
  selectedId,
  onSelect,
}: ExpedientesListProps) {
  return (
    <section className="panel list-panel">
      <div className="section-header">
        <h2>Expedientes</h2>
        <span className="count-pill">{expedientes.length}</span>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Codigo</th>
              <th>Fecha</th>
              <th>Proveedor</th>
              <th>O/S</th>
              <th>Monto</th>
              <th>Estado</th>
              <th>Veredicto</th>
              <th>Alertas</th>
            </tr>
          </thead>
          <tbody>
            {expedientes.map((expediente) => (
              <tr
                className={selectedId === expediente.id ? "selected-row" : ""}
                key={expediente.id}
                onClick={() => onSelect(expediente)}
              >
                <td>
                  <strong>{expediente.codigo_interno}</strong>
                  <span>{expediente.archivo_original}</span>
                </td>
                <td>{formatDate(expediente.fecha_carga)}</td>
                <td>{expediente.proveedor ?? "-"}</td>
                <td>{maskSensitive(expediente.numero_orden_servicio)}</td>
                <td>{formatMoney(expediente.monto_total)}</td>
                <td>
                  <StatusBadge value={expediente.estado_procesamiento} />
                </td>
                <td>
                  <StatusBadge value={expediente.veredicto_sugerido} tone="verdict" />
                </td>
                <td>{expediente.alertas}</td>
              </tr>
            ))}
            {expedientes.length === 0 && (
              <tr>
                <td colSpan={8}>Todavia no hay expedientes cargados.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
