from dataclasses import asdict, dataclass
from datetime import datetime


@dataclass(frozen=True)
class ExtractedDatum:
    field: str
    value: str
    normalized_value: str
    source: str
    page: int
    confidence: float
    evidence: str
    method: str = "regex"

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ExtractedDatum":
        return cls(
            field=str(data["field"]),
            value=str(data["value"]),
            normalized_value=str(data["normalized_value"]),
            source=str(data["source"]),
            page=int(data["page"]),
            confidence=float(data["confidence"]),
            evidence=str(data["evidence"]),
            method=str(data.get("method", "regex")),
        )


@dataclass(frozen=True)
class DataExtractionResult:
    expediente_id: int
    status: str
    fields: list[ExtractedDatum]
    extracted_at: datetime

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["extracted_at"] = self.extracted_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "DataExtractionResult":
        return cls(
            expediente_id=int(data["expediente_id"]),
            status=str(data["status"]),
            fields=[ExtractedDatum.from_dict(item) for item in data.get("fields", [])],
            extracted_at=datetime.fromisoformat(str(data["extracted_at"])),
        )
