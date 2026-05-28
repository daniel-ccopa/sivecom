import type { ValidationItem } from "../types";
import { StatusBadge } from "./StatusBadge";

type ChecklistTableProps = {
  validations: ValidationItem[];
};

export function ChecklistTable({ validations }: ChecklistTableProps) {
  return (
    <section className="panel">
      <div className="section-header">
        <h2>Checklist de validaciones</h2>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Regla</th>
              <th>Resultado</th>
              <th>Severidad</th>
              <th>Mensaje</th>
              <th>Evidencia</th>
              <th>Campos / documentos</th>
              <th>Recomendacion</th>
            </tr>
          </thead>
          <tbody>
            {validations.map((item) => (
              <tr key={item.rule_id}>
                <td>
                  <strong>{item.rule_id}</strong>
                  <span>{item.tipo.replaceAll("_", " ")}</span>
                </td>
                <td>
                  <StatusBadge value={item.resultado} tone="result" />
                </td>
                <td>
                  <StatusBadge value={item.severidad} tone="severity" />
                </td>
                <td>{item.mensaje}</td>
                <td>
                  {item.evidencia.length > 0
                    ? item.evidencia.slice(0, 3).map((evidence, index) => (
                        <p className="evidence-line" key={`${item.rule_id}-${index}`}>
                          Pag. {evidence.page ?? "-"}{" "}
                          {evidence.document_type
                            ? `(${evidence.document_type.replaceAll("_", " ")})`
                            : ""}
                          : {evidence.text || "-"}
                        </p>
                      ))
                    : "-"}
                </td>
                <td>{item.affected_fields.map((field) => field.replaceAll("_", " ")).join(", ") || "-"}</td>
                <td>{item.recomendacion}</td>
              </tr>
            ))}
            {validations.length === 0 && (
              <tr>
                <td colSpan={7}>No hay validaciones registradas.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
