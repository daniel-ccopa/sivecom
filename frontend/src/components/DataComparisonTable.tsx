import type { ExtractedDatum } from "../types";
import { labelize, maskSensitive } from "../utils/format";
import { StatusBadge } from "./StatusBadge";

type DataComparisonTableProps = {
  fields: ExtractedDatum[];
};

const COLUMNS = [
  { source: "carta_solicitud", label: "Carta" },
  { source: "orden_servicio", label: "O/S" },
  { source: "recibo_honorarios", label: "Recibo" },
  { source: "informe_actividades", label: "Informe" },
];

const COMPARABLE_FIELDS = [
  "numero_orden_servicio",
  "ruc",
  "proveedor",
  "monto_total_os",
  "monto_entregable",
  "concepto",
  "descripcion_servicio",
];

export function DataComparisonTable({ fields }: DataComparisonTableProps) {
  return (
    <section className="panel">
      <div className="section-header">
        <h2>Comparacion por documento</h2>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Campo</th>
              {COLUMNS.map((column) => (
                <th key={column.source}>{column.label}</th>
              ))}
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            {COMPARABLE_FIELDS.map((fieldName) => {
              const values = COLUMNS.map((column) =>
                fields.find((field) => field.field === fieldName && field.source === column.source),
              );
              const presentValues = values.filter(Boolean) as ExtractedDatum[];
              const uniqueValues = new Set(
                presentValues.map((field) => comparableValue(field)).filter(Boolean),
              );
              const hasConflict = uniqueValues.size > 1 && isStrictComparable(fieldName);
              const status = hasConflict
                ? "conflicto"
                : presentValues.length > 0
                  ? "ok"
                  : "no encontrado";

              return (
                <tr key={fieldName}>
                  <td>
                    <strong>{labelize(fieldName)}</strong>
                  </td>
                  {values.map((field, index) => (
                    <td key={`${fieldName}-${COLUMNS[index].source}`}>
                      {field ? maskSensitive(displayValue(field)) : "-"}
                    </td>
                  ))}
                  <td>
                    <StatusBadge value={status} />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function displayValue(field: ExtractedDatum): string {
  if (["proveedor", "concepto", "descripcion_servicio"].includes(field.field)) {
    return field.value;
  }
  return field.normalized_value || field.value;
}

function comparableValue(field: ExtractedDatum): string {
  if (field.field === "proveedor") {
    return field.normalized_value;
  }
  if (["concepto", "descripcion_servicio"].includes(field.field)) {
    return "";
  }
  return field.normalized_value || field.value;
}

function isStrictComparable(fieldName: string): boolean {
  return ["numero_orden_servicio", "ruc"].includes(fieldName);
}
