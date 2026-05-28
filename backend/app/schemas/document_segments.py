from datetime import datetime

from pydantic import BaseModel


class DocumentSegmentResponse(BaseModel):
    document_type: str
    page_start: int
    page_end: int
    text: str
    confidence: float
    evidence: list[str]


class DocumentSegmentationResponse(BaseModel):
    expediente_id: int
    status: str
    segmented_at: datetime
    segments: list[DocumentSegmentResponse]
