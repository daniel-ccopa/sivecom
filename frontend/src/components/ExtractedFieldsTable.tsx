import type { ExtractedDatum } from "../types";
import { labelize, maskSensitive } from "../utils/format";

type ExtractedFieldsTableProps = {
  fields: ExtractedDatum[];
};

export function ExtractedFieldsTable({ fields }: ExtractedFieldsTableProps) {
  function displayValue(field: ExtractedDatum): string {
    if (
      [
        "proveedor",
        "concepto",
        "descripcion_servicio",
        "numero_entregables",
        "porcentaje_entregable",
      ].includes(field.field)
    ) {
      return field.value;
    }
    return field.normalized_value || field.value;
  }

  return (
    <section className="panel">
      <div className="section-header">
        <h2>Datos extraidos</h2>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Campo</th>
              <th>Valor</th>
              <th>Fuente</th>
              <th>Pagina</th>
              <th>Confianza</th>
            </tr>
          </thead>
          <tbody>
            {fields.map((field, index) => (
              <tr key={`${field.field}-${field.page}-${index}`}>
                <td>{labelize(field.field)}</td>
                <td>{maskSensitive(displayValue(field))}</td>
                <td>{labelize(field.source)}</td>
                <td>{field.page}</td>
                <td>{Math.round(field.confidence * 100)}%</td>
              </tr>
            ))}
            {fields.length === 0 && (
              <tr>
                <td colSpan={5}>No hay datos extraidos registrados.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
