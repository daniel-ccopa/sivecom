import type { DocumentSegment } from "../types";
import { labelize } from "../utils/format";
import { StatusBadge } from "./StatusBadge";

type DocumentsTableProps = {
  segments: DocumentSegment[];
};

export function DocumentsTable({ segments }: DocumentsTableProps) {
  return (
    <section className="panel">
      <div className="section-header">
        <h2>Documentos detectados</h2>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Documento</th>
              <th>Paginas</th>
              <th>Confianza</th>
              <th>Evidencia</th>
            </tr>
          </thead>
          <tbody>
            {segments.map((segment, index) => (
              <tr key={`${segment.document_type}-${segment.page_start}-${index}`}>
                <td>
                  <StatusBadge value={segment.document_type} />
                </td>
                <td>
                  {segment.page_start === segment.page_end
                    ? segment.page_start
                    : `${segment.page_start}-${segment.page_end}`}
                </td>
                <td>{Math.round(segment.confidence * 100)}%</td>
                <td>{segment.evidence.map(labelize).join(", ") || "-"}</td>
              </tr>
            ))}
            {segments.length === 0 && (
              <tr>
                <td colSpan={4}>No hay segmentos registrados.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
