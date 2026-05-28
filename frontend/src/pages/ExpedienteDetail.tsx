import { FileText } from "lucide-react";

import { AlertsTable } from "../components/AlertsTable";
import { ChecklistTable } from "../components/ChecklistTable";
import { DataComparisonTable } from "../components/DataComparisonTable";
import { DocumentsTable } from "../components/DocumentsTable";
import { ExportReportButton } from "../components/ExportReportButton";
import { ExtractedFieldsTable } from "../components/ExtractedFieldsTable";
import { PdfViewer } from "../components/PdfViewer";
import { ProcessingNotice } from "../components/ProcessingNotice";
import { RequiredDocumentsPanel } from "../components/RequiredDocumentsPanel";
import { StatusBadge } from "../components/StatusBadge";
import { VerdictCard } from "../components/VerdictCard";
import type { ExpedienteDetailData } from "../types";
import { formatBytes, formatDate } from "../utils/format";

type ExpedienteDetailProps = {
  detail: ExpedienteDetailData | null;
  loading: boolean;
  isReprocessing: boolean;
  onReprocess: () => void;
};

export function ExpedienteDetail({
  detail,
  loading,
  isReprocessing,
  onReprocess,
}: ExpedienteDetailProps) {
  if (loading) {
    return <section className="panel empty-detail">Cargando expediente...</section>;
  }

  if (!detail) {
    return (
      <section className="panel empty-detail">
        <FileText size={32} />
        <p>Selecciona un expediente para revisar sus resultados.</p>
      </section>
    );
  }

  const alerts =
    detail.validaciones?.validations.filter((item) => item.resultado !== "OK") ?? [];

  return (
    <div className="detail-grid">
      <section className="panel expediente-summary">
        <div>
          <p className="eyebrow">Expediente</p>
          <h1>{detail.expediente.codigo_interno}</h1>
          <p>{detail.expediente.archivo_original}</p>
        </div>
        <div className="summary-actions">
          <StatusBadge value={detail.expediente.estado_procesamiento} />
          <ExportReportButton detail={detail} />
        </div>
        <dl className="metadata-grid">
          <div>
            <dt>Fecha de carga</dt>
            <dd>{formatDate(detail.expediente.fecha_carga)}</dd>
          </div>
          <div>
            <dt>Tamano</dt>
            <dd>{formatBytes(detail.expediente.tamano_bytes)}</dd>
          </div>
          <div>
            <dt>Alertas</dt>
            <dd>{alerts.length}</dd>
          </div>
        </dl>
      </section>

      <VerdictCard validation={detail.validaciones} />
      {detail.expediente.estado_procesamiento !== "procesado" && (
        <section className="panel notice-panel">
          <FileText size={20} />
          <div>
            <h2>Procesamiento en segundo plano</h2>
            <p>
              El PDF ya fue cargado. El sistema esta extrayendo texto, clasificando documentos y validando datos.
            </p>
          </div>
        </section>
      )}
      <PdfViewer expediente={detail.expediente} />
      <ProcessingNotice
        isReprocessing={isReprocessing}
        textResult={detail.texto}
        onReprocess={onReprocess}
      />
      <AlertsTable alerts={alerts} />
      <RequiredDocumentsPanel data={detail.datos} segmentation={detail.segmentos} />
      <DataComparisonTable fields={detail.datos?.fields ?? []} />
      <ChecklistTable validations={detail.validaciones?.validations ?? []} />
      <ExtractedFieldsTable fields={detail.datos?.fields ?? []} />
      <DocumentsTable segments={detail.segmentos?.segments ?? []} />
    </div>
  );
}
