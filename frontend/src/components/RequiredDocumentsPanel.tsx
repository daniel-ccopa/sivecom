import type { DataExtractionResponse, DocumentSegmentationResponse } from "../types";
import { labelize } from "../utils/format";
import { StatusBadge } from "./StatusBadge";

type RequiredDocumentsPanelProps = {
  data: DataExtractionResponse | null;
  segmentation: DocumentSegmentationResponse | null;
};

const REQUIRED_DOCUMENTS = [
  { types: ["carta_solicitud"], label: "Carta" },
  { types: ["orden_servicio"], label: "Orden de servicio" },
  { types: ["informe_actividades"], label: "Informe" },
  { types: ["recibo_honorarios", "factura"], label: "Recibo / factura" },
];

const IMPORTANT_FIELDS = [
  "numero_orden_servicio",
  "ruc",
  "proveedor",
  "monto_total_os",
  "monto_entregable",
  "concepto",
  "descripcion_servicio",
];

export function RequiredDocumentsPanel({
  data,
  segmentation,
}: RequiredDocumentsPanelProps) {
  const fields = data?.fields ?? [];
  const segments = segmentation?.segments ?? [];

  return (
    <section className="panel">
      <div className="section-header">
        <h2>Documentos obligatorios</h2>
      </div>
      <div className="required-doc-grid">
        {REQUIRED_DOCUMENTS.map((document) => {
          const documentSegments = segments.filter(
            (segment) => document.types.includes(segment.document_type),
          );
          const documentFields = fields.filter((field) =>
            document.types.includes(field.source),
          );
          const present = documentSegments.length > 0;
          return (
            <article className="required-doc-card" key={document.label}>
              <div className="required-doc-head">
                <h3>{document.label}</h3>
                <StatusBadge value={present ? "detectado" : "no encontrado"} />
              </div>
              <p>
                Paginas:{" "}
                <strong>
                  {documentSegments.map(formatSegmentPages).join(", ") || "-"}
                </strong>
              </p>
              <p>
                Confianza:{" "}
                <strong>
                  {present
                    ? `${Math.round(Math.max(...documentSegments.map((item) => item.confidence)) * 100)}%`
                    : "-"}
                </strong>
              </p>
              <div className="field-chip-row">
                {IMPORTANT_FIELDS.map((fieldName) => {
                  const found = documentFields.some((field) => field.field === fieldName);
                  return (
                    <span
                      className={`field-chip ${found ? "field-chip-ok" : "field-chip-missing"}`}
                      key={`${document.label}-${fieldName}`}
                    >
                      {labelize(fieldName)}
                    </span>
                  );
                })}
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}

function formatSegmentPages(segment: { page_start: number; page_end: number }): string {
  return segment.page_start === segment.page_end
    ? String(segment.page_start)
    : `${segment.page_start}-${segment.page_end}`;
}
