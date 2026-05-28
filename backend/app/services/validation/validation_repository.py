import json
from pathlib import Path

from app.models.validation_result import ValidationRun


class ValidationRepository:
    def __init__(self, validation_dir: Path) -> None:
        self.validation_dir = validation_dir

    def save(self, result: ValidationRun) -> ValidationRun:
        self.validation_dir.mkdir(parents=True, exist_ok=True)
        target = self._path_for(result.expediente_id)
        with target.open("w", encoding="utf-8") as file:
            json.dump(result.to_dict(), file, ensure_ascii=True, indent=2)
        return result

    def get_by_expediente_id(self, expediente_id: int) -> ValidationRun | None:
        target = self._path_for(expediente_id)
        if not target.exists():
            return None

        with target.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        return ValidationRun.from_dict(payload)

    def _path_for(self, expediente_id: int) -> Path:
        return self.validation_dir / f"expediente_{expediente_id:06d}.json"
