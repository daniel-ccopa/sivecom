import json
from pathlib import Path

from app.models.text_extraction import TextExtractionResult


class TextExtractionRepository:
    def __init__(self, text_extraction_dir: Path) -> None:
        self.text_extraction_dir = text_extraction_dir

    def save(self, result: TextExtractionResult) -> TextExtractionResult:
        self.text_extraction_dir.mkdir(parents=True, exist_ok=True)
        target = self._path_for(result.expediente_id)
        with target.open("w", encoding="utf-8") as file:
            json.dump(result.to_dict(), file, ensure_ascii=True, indent=2)
        return result

    def get_by_expediente_id(self, expediente_id: int) -> TextExtractionResult | None:
        target = self._path_for(expediente_id)
        if not target.exists():
            return None

        with target.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        return TextExtractionResult.from_dict(payload)

    def _path_for(self, expediente_id: int) -> Path:
        return self.text_extraction_dir / f"expediente_{expediente_id:06d}.json"
