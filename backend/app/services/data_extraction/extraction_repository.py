import json
from pathlib import Path

from app.models.extracted_data import DataExtractionResult


class DataExtractionRepository:
    def __init__(self, data_extraction_dir: Path) -> None:
        self.data_extraction_dir = data_extraction_dir

    def save(self, result: DataExtractionResult) -> DataExtractionResult:
        self.data_extraction_dir.mkdir(parents=True, exist_ok=True)
        target = self._path_for(result.expediente_id)
        with target.open("w", encoding="utf-8") as file:
            json.dump(result.to_dict(), file, ensure_ascii=True, indent=2)
        return result

    def get_by_expediente_id(self, expediente_id: int) -> DataExtractionResult | None:
        target = self._path_for(expediente_id)
        if not target.exists():
            return None

        with target.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        return DataExtractionResult.from_dict(payload)

    def list_all(
        self,
        exclude_expediente_id: int | None = None,
    ) -> list[DataExtractionResult]:
        if not self.data_extraction_dir.exists():
            return []

        results: list[DataExtractionResult] = []
        for path in sorted(self.data_extraction_dir.glob("expediente_*.json")):
            with path.open("r", encoding="utf-8") as file:
                result = DataExtractionResult.from_dict(json.load(file))
            if result.expediente_id == exclude_expediente_id:
                continue
            results.append(result)
        return results

    def _path_for(self, expediente_id: int) -> Path:
        return self.data_extraction_dir / f"expediente_{expediente_id:06d}.json"
