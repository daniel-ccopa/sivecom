import { ExternalLink, FileText } from "lucide-react";

import { getPdfUrl } from "../services/api";
import type { ExpedienteListItem } from "../types";

type PdfViewerProps = {
  expediente: ExpedienteListItem;
};

export function PdfViewer({ expediente }: PdfViewerProps) {
  const pdfUrl = getPdfUrl(expediente.id);

  return (
    <section className="panel pdf-panel">
      <div className="section-header">
        <h2>PDF del expediente</h2>
        <a className="button secondary compact" href={pdfUrl} rel="noreferrer" target="_blank">
          <ExternalLink size={15} />
          Abrir
        </a>
      </div>
      <div className="pdf-frame-wrap">
        <iframe
          src={pdfUrl}
          title={`PDF ${expediente.codigo_interno}`}
        />
        <div className="pdf-fallback">
          <FileText size={26} />
          <p>Si el navegador no muestra el PDF, usa el boton Abrir.</p>
        </div>
      </div>
    </section>
  );
}
