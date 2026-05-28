import json
import threading
from datetime import datetime, timezone
from json import JSONDecodeError
from pathlib import Path

from app.models.expediente import Expediente
from app.services.storage.file_storage import SavedFile


class ExpedienteRepository:
    _lock = threading.Lock()

    def __init__(self, metadata_dir: Path) -> None:
        self.metadata_dir = metadata_dir
        self.metadata_file = metadata_dir / "expedientes.json"

    def create_from_upload(self, saved_file: SavedFile) -> Expediente:
        with self._lock:
            expedientes = self._read_all()
            next_id = self._next_id(expedientes)
            expediente = Expediente(
                id=next_id,
                codigo_interno=f"SIV-{next_id:06d}",
                archivo_original=saved_file.original_filename,
                archivo_guardado=saved_file.stored_filename,
                tamano_bytes=saved_file.size_bytes,
                fecha_carga=datetime.now(timezone.utc),
                estado="pendiente",
                sha256=saved_file.sha256,
                content_type=saved_file.content_type,
            )
            expedientes.append(expediente)
            self._write_all(expedientes)
            return expediente

    def list_all(self) -> list[Expediente]:
        return self._read_all()

    def get_by_id(self, expediente_id: int) -> Expediente | None:
        for expediente in self._read_all():
            if expediente.id == expediente_id:
                return expediente
        return None

    def _read_all(self) -> list[Expediente]:
        if not self.metadata_file.exists():
            return []

        try:
            with self.metadata_file.open("r", encoding="utf-8") as file:
                raw_items = json.load(file)
        except JSONDecodeError as exc:
            raise RuntimeError("El archivo de metadatos de expedientes esta dañado.") from exc

        return [Expediente.from_dict(item) for item in raw_items]

    def _write_all(self, expedientes: list[Expediente]) -> None:
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        payload = [expediente.to_dict() for expediente in expedientes]
        temp_file = self.metadata_file.with_suffix(".json.tmp")
        with temp_file.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=True, indent=2)
        temp_file.replace(self.metadata_file)

    @staticmethod
    def _next_id(expedientes: list[Expediente]) -> int:
        if not expedientes:
            return 1
        return max(expediente.id for expediente in expedientes) + 1
