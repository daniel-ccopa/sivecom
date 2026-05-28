import type {
  DataExtractionResponse,
  DocumentSegmentationResponse,
  ExpedienteListItem,
  ExpedienteUploadResponse,
  TextExtractionResponse,
  ValidationRunResponse,
} from "../types";

const API_BASE_URL = resolveApiBaseUrl(import.meta.env.VITE_API_BASE_URL);

function resolveApiBaseUrl(configuredUrl?: string): string {
  const cleanUrl = configuredUrl?.trim().replace(/\/+$/, "");
  if (!cleanUrl) {
    return defaultApiBaseUrl();
  }
  if (typeof window === "undefined") {
    return cleanUrl;
  }

  let configured: URL;
  try {
    configured = new URL(cleanUrl);
  } catch {
    return defaultApiBaseUrl();
  }

  const pageHost = window.location.hostname;
  const configuredIsLoopback = ["localhost", "127.0.0.1"].includes(configured.hostname);
  const pageIsLoopback = ["localhost", "127.0.0.1"].includes(pageHost);

  if (configuredIsLoopback && !pageIsLoopback) {
    configured.hostname = pageHost;
  }

  return configured.toString().replace(/\/+$/, "");
}

function defaultApiBaseUrl(): string {
  if (typeof window === "undefined") {
    return "http://localhost:8000";
  }
  return `${window.location.protocol}//${window.location.hostname}:8000`;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, init);
    if (!response.ok) {
      const detail = await response.text();
      throw new Error(detail || `Error HTTP ${response.status}`);
    }
    return response.json() as Promise<T>;
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error(
        `No se pudo conectar con la API en ${API_BASE_URL}. Verifica que el backend este ejecutandose en el puerto 8000.`,
      );
    }
    throw error;
  }
}

export async function listExpedientes(): Promise<ExpedienteListItem[]> {
  return request<ExpedienteListItem[]>("/expedientes");
}

export async function uploadExpediente(file: File): Promise<ExpedienteUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  return request<ExpedienteUploadResponse>("/expedientes/upload", {
    method: "POST",
    body: formData,
  });
}

export async function getDatos(expedienteId: number): Promise<DataExtractionResponse> {
  return request<DataExtractionResponse>(`/expedientes/${expedienteId}/datos`);
}

export async function getTexto(expedienteId: number): Promise<TextExtractionResponse> {
  return request<TextExtractionResponse>(`/expedientes/${expedienteId}/texto`);
}

export async function getSegmentos(
  expedienteId: number,
): Promise<DocumentSegmentationResponse> {
  return request<DocumentSegmentationResponse>(`/expedientes/${expedienteId}/segmentos`);
}

export async function getValidaciones(
  expedienteId: number,
): Promise<ValidationRunResponse> {
  return request<ValidationRunResponse>(`/expedientes/${expedienteId}/validaciones`);
}

export async function reprocessExpediente(expedienteId: number): Promise<ExpedienteListItem> {
  return request<ExpedienteListItem>(`/expedientes/${expedienteId}/reprocess`, {
    method: "POST",
  });
}

export function getPdfUrl(expedienteId: number): string {
  return `${API_BASE_URL}/expedientes/${expedienteId}/pdf`;
}
