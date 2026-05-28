import { AlertTriangle, RotateCw } from "lucide-react";

import type { TextExtractionResponse } from "../types";

type ProcessingNoticeProps = {
  textResult: TextExtractionResponse | null;
  isReprocessing: boolean;
  onReprocess: () => void;
};

export function ProcessingNotice({
  textResult,
  isReprocessing,
  onReprocess,
}: ProcessingNoticeProps) {
  if (!textResult || textResult.status === "extraido" || textResult.status === "extraido_con_ocr") {
    return null;
  }

  const isOcrError = textResult.status === "error_ocr";
  return (
    <section className={`panel notice-panel ${isOcrError ? "notice-error" : ""}`}>
      <AlertTriangle size={20} />
      <div>
        <h2>{isOcrError ? "OCR no disponible" : "Texto no extraido"}</h2>
        <p>
          {textResult.error ??
            "No se encontro texto digital suficiente para extraer informacion."}
        </p>
        {isOcrError && (
          <p>
            Este PDF parece escaneado. Instala PaddleOCR y PaddlePaddle con las dependencias del backend, luego reprocesa el expediente.
          </p>
        )}
      </div>
      <button className="button secondary" disabled={isReprocessing} onClick={onReprocess}>
        <RotateCw size={16} />
        {isReprocessing ? "Reprocesando" : "Reprocesar"}
      </button>
    </section>
  );
}
