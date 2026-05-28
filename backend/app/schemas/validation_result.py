from datetime import datetime

from pydantic import BaseModel


class ValidationEvidenceResponse(BaseModel):
    text: str
    page: int | None = None
    document_type: str | None = None
    field: str | None = None


class ValidationItemResponse(BaseModel):
    rule_id: str
    tipo: str
    resultado: str
    severidad: str
    mensaje: str
    evidencia: list[ValidationEvidenceResponse]
    recomendacion: str
    passed: bool
    affected_fields: list[str]


class ValidationRunResponse(BaseModel):
    expediente_id: int
    verdict: str
    summary: dict[str, int]
    validations: list[ValidationItemResponse]
    validated_at: datetime
