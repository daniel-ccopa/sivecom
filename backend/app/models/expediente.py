from dataclasses import asdict, dataclass
from datetime import datetime


@dataclass(frozen=True)
class Expediente:
    id: int
    codigo_interno: str
    archivo_original: str
    archivo_guardado: str
    tamano_bytes: int
    fecha_carga: datetime
    estado: str
    sha256: str
    content_type: str | None = None

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["fecha_carga"] = self.fecha_carga.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Expediente":
        return cls(
            id=int(data["id"]),
            codigo_interno=str(data["codigo_interno"]),
            archivo_original=str(data["archivo_original"]),
            archivo_guardado=str(data["archivo_guardado"]),
            tamano_bytes=int(data["tamano_bytes"]),
            fecha_carga=datetime.fromisoformat(str(data["fecha_carga"])),
            estado=str(data["estado"]),
            sha256=str(data["sha256"]),
            content_type=(
                str(data["content_type"]) if data.get("content_type") is not None else None
            ),
        )
