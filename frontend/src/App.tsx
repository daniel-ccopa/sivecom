import { RefreshCw } from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { ExpedienteDetail } from "./pages/ExpedienteDetail";
import { ExpedienteUpload } from "./pages/ExpedienteUpload";
import { ExpedientesList } from "./pages/ExpedientesList";
import {
  getDatos,
  getSegmentos,
  getTexto,
  getValidaciones,
  listExpedientes,
  reprocessExpediente,
} from "./services/api";
import type { ExpedienteDetailData, ExpedienteListItem } from "./types";

function App() {
  const [expedientes, setExpedientes] = useState<ExpedienteListItem[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [detail, setDetail] = useState<ExpedienteDetailData | null>(null);
  const [loadingList, setLoadingList] = useState(false);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [isReprocessing, setIsReprocessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const selectedIdRef = useRef<number | null>(null);

  const selectedExpediente = useMemo(
    () => expedientes.find((item) => item.id === selectedId) ?? null,
    [expedientes, selectedId],
  );

  useEffect(() => {
    selectedIdRef.current = selectedId;
  }, [selectedId]);

  const refreshList = useCallback(async (nextSelectedId?: number, silent = false) => {
    if (!silent) {
      setLoadingList(true);
    }
    setError(null);
    try {
      const items = await listExpedientes();
      setExpedientes(items);
      const candidateId = nextSelectedId ?? selectedIdRef.current ?? items[0]?.id ?? null;
      setSelectedId(candidateId);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "No se pudo cargar la lista de expedientes.",
      );
    } finally {
      if (!silent) {
        setLoadingList(false);
      }
    }
  }, []);

  const loadDetail = useCallback(async (expediente: ExpedienteListItem, silent = false) => {
    if (!silent) {
      setLoadingDetail(true);
    }
    setError(null);
    try {
      const [texto, datos, segmentos, validaciones] = await Promise.all([
        getTexto(expediente.id).catch(() => null),
        getDatos(expediente.id).catch(() => null),
        getSegmentos(expediente.id).catch(() => null),
        getValidaciones(expediente.id).catch(() => null),
      ]);
      setDetail({
        expediente,
        texto,
        datos,
        segmentos,
        validaciones,
      });
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "No se pudo cargar el detalle.",
      );
    } finally {
      if (!silent) {
        setLoadingDetail(false);
      }
    }
  }, []);

  useEffect(() => {
    void refreshList();
  }, [refreshList]);

  useEffect(() => {
    const hasPendingProcessing = expedientes.some(
      (item) => item.estado_procesamiento !== "procesado",
    );
    if (!hasPendingProcessing) {
      return;
    }

    const interval = window.setInterval(() => {
      void refreshList(selectedId ?? undefined, true);
    }, 5000);

    return () => window.clearInterval(interval);
  }, [expedientes, refreshList, selectedId]);

  useEffect(() => {
    if (!selectedExpediente) {
      setDetail(null);
      return;
    }

    void loadDetail(selectedExpediente);
  }, [loadDetail, selectedId]);

  useEffect(() => {
    if (!selectedExpediente) {
      return;
    }

    setDetail((current) =>
      current && current.expediente.id === selectedExpediente.id
        ? { ...current, expediente: selectedExpediente }
        : current,
    );
  }, [selectedExpediente]);

  useEffect(() => {
    if (!selectedExpediente || selectedExpediente.estado_procesamiento === "procesado") {
      return;
    }

    const interval = window.setInterval(() => {
      void loadDetail(selectedExpediente, true);
    }, 5000);

    return () => window.clearInterval(interval);
  }, [loadDetail, selectedExpediente]);

  async function handleReprocess() {
    if (!selectedId) {
      return;
    }
    setIsReprocessing(true);
    setError(null);
    try {
      await reprocessExpediente(selectedId);
      await refreshList(selectedId);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "No se pudo reprocesar el expediente.",
      );
    } finally {
      setIsReprocessing(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">SIVECOM</p>
          <h1>Dashboard administrativo</h1>
        </div>
        <button className="button secondary" disabled={loadingList} onClick={() => refreshList()}>
          <RefreshCw size={16} />
          Actualizar
        </button>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <div className="layout-grid">
        <aside className="sidebar">
          <ExpedienteUpload onUploaded={(id) => refreshList(id)} />
          {loadingList ? (
            <section className="panel">Cargando expedientes...</section>
          ) : (
            <ExpedientesList
              expedientes={expedientes}
              selectedId={selectedId}
              onSelect={(expediente) => setSelectedId(expediente.id)}
            />
          )}
        </aside>
        <section className="content-area">
          <ExpedienteDetail
            detail={detail}
            isReprocessing={isReprocessing}
            loading={loadingDetail}
            onReprocess={handleReprocess}
          />
        </section>
      </div>
    </main>
  );
}

export default App;
