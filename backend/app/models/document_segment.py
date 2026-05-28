from dataclasses import asdict, dataclass
from datetime import datetime


@dataclass(frozen=True)
class DocumentSegment:
    document_type: str
    page_start: int
    page_end: int
    text: str
    confidence: float
    evidence: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "DocumentSegment":
        return cls(
            document_type=str(data["document_type"]),
            page_start=int(data["page_start"]),
            page_end=int(data["page_end"]),
            text=str(data["text"]),
            confidence=float(data["confidence"]),
            evidence=[str(item) for item in data.get("evidence", [])],
        )


@dataclass(frozen=True)
class DocumentSegmentationResult:
    expediente_id: int
    status: str
    segments: list[DocumentSegment]
    segmented_at: datetime

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["segmented_at"] = self.segmented_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "DocumentSegmentationResult":
        return cls(
            expediente_id=int(data["expediente_id"]),
            status=str(data["status"]),
            segments=[
                DocumentSegment.from_dict(segment)
                for segment in data.get("segments", [])
            ],
            segmented_at=datetime.fromisoformat(str(data["segmented_at"])),
        )
