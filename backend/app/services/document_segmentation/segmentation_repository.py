import json
from pathlib import Path

from app.models.document_segment import DocumentSegmentationResult


class SegmentationRepository:
    def __init__(self, segmentation_dir: Path) -> None:
        self.segmentation_dir = segmentation_dir

    def save(self, result: DocumentSegmentationResult) -> DocumentSegmentationResult:
        self.segmentation_dir.mkdir(parents=True, exist_ok=True)
        target = self._path_for(result.expediente_id)
        with target.open("w", encoding="utf-8") as file:
            json.dump(result.to_dict(), file, ensure_ascii=True, indent=2)
        return result

    def get_by_expediente_id(self, expediente_id: int) -> DocumentSegmentationResult | None:
        target = self._path_for(expediente_id)
        if not target.exists():
            return None

        with target.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        return DocumentSegmentationResult.from_dict(payload)

    def _path_for(self, expediente_id: int) -> Path:
        return self.segmentation_dir / f"expediente_{expediente_id:06d}.json"
