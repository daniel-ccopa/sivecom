export type ExpedienteListItem = {
  id: number;
  codigo_interno: string;
  archivo_original: string;
  tamano_bytes: number;
  fecha_carga: string;
  estado: string;
  estado_procesamiento: string;
  veredicto_sugerido: string | null;
  alertas: number;
  proveedor: string | null;
  numero_orden_servicio: string | null;
  monto_total: string | null;
};

export type ExpedienteUploadResponse = {
  id: number;
  codigo_interno: string;
  archivo_original: string;
  tamano_bytes: number;
  fecha_carga: string;
  estado: string;
};

export type ExtractedDatum = {
  field: string;
  value: string;
  normalized_value: string;
  source: string;
  page: number;
  confidence: number;
  evidence: string;
  method: string;
};

export type DataExtractionResponse = {
  expediente_id: number;
  status: string;
  extracted_at: string;
  fields: ExtractedDatum[];
};

export type DocumentSegment = {
  document_type: string;
  page_start: number;
  page_end: number;
  text: string;
  confidence: number;
  evidence: string[];
};

export type DocumentSegmentationResponse = {
  expediente_id: number;
  status: string;
  segmented_at: string;
  segments: DocumentSegment[];
};

export type ExtractedPageText = {
  page_number: number;
  text: string;
  char_count: number;
  extraction_method: string;
  ocr_used: boolean;
  ocr_confidence: number | null;
  error: string | null;
};

export type TextExtractionResponse = {
  expediente_id: number;
  status: string;
  total_pages: number;
  total_char_count: number;
  extracted_at: string;
  pages: ExtractedPageText[];
  error: string | null;
};

export type ValidationEvidence = {
  text: string;
  page: number | null;
  document_type: string | null;
  field: string | null;
};

export type ValidationItem = {
  rule_id: string;
  tipo: string;
  resultado: string;
  severidad: string;
  mensaje: string;
  evidencia: ValidationEvidence[];
  recomendacion: string;
  passed: boolean;
  affected_fields: string[];
};

export type ValidationRunResponse = {
  expediente_id: number;
  verdict: string;
  summary: Record<string, number>;
  validations: ValidationItem[];
  validated_at: string;
};

export type ExpedienteDetailData = {
  expediente: ExpedienteListItem;
  texto: TextExtractionResponse | null;
  datos: DataExtractionResponse | null;
  segmentos: DocumentSegmentationResponse | null;
  validaciones: ValidationRunResponse | null;
};
