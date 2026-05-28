from datetime import datetime

from pydantic import BaseModel


class ExtractedPageTextResponse(BaseModel):
    page_number: int
    text: str
    char_count: int
    extraction_method: str
    ocr_used: bool
    ocr_confidence: float | None = None
    error: str | None = None


class TextExtractionResponse(BaseModel):
    expediente_id: int
    status: str
    total_pages: int
    total_char_count: int
    extracted_at: datetime
    pages: list[ExtractedPageTextResponse]
    error: str | None = None
