from dataclasses import asdict, dataclass
from datetime import datetime


@dataclass(frozen=True)
class ExtractedPageText:
    page_number: int
    text: str
    char_count: int
    extraction_method: str = "direct_text"
    ocr_used: bool = False
    ocr_confidence: float | None = None
    error: str | None = None


@dataclass(frozen=True)
class TextExtractionResult:
    expediente_id: int
    status: str
    total_pages: int
    pages: list[ExtractedPageText]
    extracted_at: datetime
    error: str | None = None

    @property
    def total_char_count(self) -> int:
        return sum(page.char_count for page in self.pages)

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["extracted_at"] = self.extracted_at.isoformat()
        data["total_char_count"] = self.total_char_count
        return data

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "TextExtractionResult":
        pages = [
            ExtractedPageText(
                page_number=int(page["page_number"]),
                text=str(page["text"]),
                char_count=int(page["char_count"]),
                extraction_method=str(page.get("extraction_method", "direct_text")),
                ocr_used=bool(page.get("ocr_used", False)),
                ocr_confidence=(
                    float(page["ocr_confidence"])
                    if page.get("ocr_confidence") is not None
                    else None
                ),
                error=str(page["error"]) if page.get("error") is not None else None,
            )
            for page in data.get("pages", [])
        ]
        return cls(
            expediente_id=int(data["expediente_id"]),
            status=str(data["status"]),
            total_pages=int(data["total_pages"]),
            pages=pages,
            extracted_at=datetime.fromisoformat(str(data["extracted_at"])),
            error=str(data["error"]) if data.get("error") is not None else None,
        )
