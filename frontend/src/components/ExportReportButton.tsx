import { Download } from "lucide-react";

import type { ExpedienteDetailData } from "../types";
import { maskSensitive } from "../utils/format";

type ExportReportButtonProps = {
  detail: ExpedienteDetailData | null;
};

export function ExportReportButton({ detail }: ExportReportButtonProps) {
  function exportReport() {
    if (!detail) {
      return;
    }

    const payload = {
      generated_at: new Date().toISOString(),
      expediente: detail.expediente,
      veredicto_sugerido: detail.validaciones?.verdict ?? null,
      summary: detail.validaciones?.summary ?? null,
      datos_extraidos: detail.datos?.fields.map((field) => ({
        ...field,
        value: maskSensitive(field.value),
        normalized_value: maskSensitive(field.normalized_value),
        evidence: maskSensitive(field.evidence),
      })),
      documentos_detectados: detail.segmentos?.segments.map((segment) => ({
        document_type: segment.document_type,
        page_start: segment.page_start,
        page_end: segment.page_end,
        confidence: segment.confidence,
        evidence: segment.evidence,
      })),
      validaciones: detail.validaciones?.validations.map((validation) => ({
        ...validation,
        evidencia: validation.evidencia.map((evidence) => ({
          ...evidence,
          text: maskSensitive(evidence.text),
        })),
      })),
    };

    const blob = new Blob([JSON.stringify(payload, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${detail.expediente.codigo_interno}-informe.json`;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <button className="button secondary" disabled={!detail} onClick={exportReport}>
      <Download size={16} />
      Exportar informe
    </button>
  );
}
