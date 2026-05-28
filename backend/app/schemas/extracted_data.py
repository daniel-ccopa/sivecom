from datetime import datetime

from pydantic import BaseModel


class ExtractedDatumResponse(BaseModel):
    field: str
    value: str
    normalized_value: str
    source: str
    page: int
    confidence: float
    evidence: str
    method: str


class DataExtractionResponse(BaseModel):
    expediente_id: int
    status: str
    extracted_at: datetime
    fields: list[ExtractedDatumResponse]
