from dataclasses import asdict, dataclass
from datetime import datetime


@dataclass(frozen=True)
class ValidationEvidence:
    text: str
    page: int | None = None
    document_type: str | None = None
    field: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ValidationEvidence":
        page = data.get("page")
        return cls(
            text=str(data["text"]),
            page=int(page) if page is not None else None,
            document_type=(
                str(data["document_type"])
                if data.get("document_type") is not None
                else None
            ),
            field=str(data["field"]) if data.get("field") is not None else None,
        )


@dataclass(frozen=True)
class ValidationItem:
    rule_id: str
    tipo: str
    resultado: str
    severidad: str
    mensaje: str
    evidencia: list[ValidationEvidence]
    recomendacion: str
    passed: bool
    affected_fields: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ValidationItem":
        return cls(
            rule_id=str(data["rule_id"]),
            tipo=str(data["tipo"]),
            resultado=str(data["resultado"]),
            severidad=str(data["severidad"]),
            mensaje=str(data["mensaje"]),
            evidencia=[
                ValidationEvidence.from_dict(item)
                for item in data.get("evidencia", [])
            ],
            recomendacion=str(data["recomendacion"]),
            passed=bool(data["passed"]),
            affected_fields=[str(item) for item in data.get("affected_fields", [])],
        )


@dataclass(frozen=True)
class ValidationRun:
    expediente_id: int
    verdict: str
    summary: dict[str, int]
    validations: list[ValidationItem]
    validated_at: datetime

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["validated_at"] = self.validated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ValidationRun":
        return cls(
            expediente_id=int(data["expediente_id"]),
            verdict=str(data["verdict"]),
            summary={str(key): int(value) for key, value in data["summary"].items()},
            validations=[
                ValidationItem.from_dict(item)
                for item in data.get("validations", [])
            ],
            validated_at=datetime.fromisoformat(str(data["validated_at"])),
        )
