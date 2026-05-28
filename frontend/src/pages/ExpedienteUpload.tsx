import { Upload } from "lucide-react";
import { FormEvent, useState } from "react";

import { uploadExpediente } from "../services/api";

type ExpedienteUploadProps = {
  onUploaded: (expedienteId: number) => void;
};

export function ExpedienteUpload({ onUploaded }: ExpedienteUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) {
      setMessage("Selecciona un PDF antes de cargar.");
      return;
    }
    setIsUploading(true);
    setMessage("Cargando expediente...");
    try {
      const uploaded = await uploadExpediente(file);
      setFile(null);
      setMessage("Expediente cargado. El procesamiento continua en segundo plano.");
      onUploaded(uploaded.id);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "No se pudo cargar el PDF.");
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <section className="panel upload-panel">
      <form onSubmit={handleSubmit}>
        <label>
          <span>Cargar expediente PDF</span>
          <input
            accept="application/pdf"
            disabled={isUploading}
            type="file"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          />
        </label>
        <button className="button" disabled={isUploading} type="submit">
          <Upload size={16} />
          {isUploading ? "Procesando" : "Subir PDF"}
        </button>
      </form>
      {message && <p className="form-message">{message}</p>}
    </section>
  );
}
