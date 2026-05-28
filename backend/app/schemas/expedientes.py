from datetime import datetime

from pydantic import BaseModel


class ExpedienteUploadResponse(BaseModel):
    id: int
    codigo_interno: str
    archivo_original: str
    tamano_bytes: int
    fecha_carga: datetime
    estado: str


class ExpedienteListItemResponse(BaseModel):
    id: int
    codigo_interno: str
    archivo_original: str
    tamano_bytes: int
    fecha_carga: datetime
    estado: str
    estado_procesamiento: str
    veredicto_sugerido: str | None = None
    alertas: int
    proveedor: str | None = None
    numero_orden_servicio: str | None = None
    monto_total: str | None = None


class ExpedienteDetailResponse(ExpedienteListItemResponse):
    content_type: str | None = None
