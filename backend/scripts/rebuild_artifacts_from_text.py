from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.data_extraction.extraction_repository import DataExtractionRepository
from app.services.data_extraction.field_extractor import FieldExtractor
from app.services.document_segmentation.document_segmenter import DocumentSegmenter
from app.services.document_segmentation.segmentation_repository import SegmentationRepository
from app.services.pdf_processing.text_extraction_repository import TextExtractionRepository
from app.services.validation.validation_engine import ValidationEngine
from app.services.validation.validation_repository import ValidationRepository


def main() -> None:
    storage_dir = Path("storage")
    text_repo = TextExtractionRepository(storage_dir / "text_extractions")
    segmentation_repo = SegmentationRepository(storage_dir / "segmentations")
    data_repo = DataExtractionRepository(storage_dir / "data_extractions")
    validation_repo = ValidationRepository(storage_dir / "validations")

    paths = sorted((storage_dir / "text_extractions").glob("expediente_*.json"))
    regenerated = 0
    for path in paths:
        expediente_id = int(path.stem.split("_")[1])
        text_result = text_repo.get_by_expediente_id(expediente_id)
        if text_result is None:
            continue

        segmentation = DocumentSegmenter().segment(text_result)
        segmentation_repo.save(segmentation)

        extraction = FieldExtractor().extract(segmentation)
        data_repo.save(extraction)

        validation = ValidationEngine().evaluate(
            segmentation=segmentation,
            extraction=extraction,
            previous_extractions=data_repo.list_all(exclude_expediente_id=expediente_id),
        )
        validation_repo.save(validation)
        regenerated += 1

    print(f"Regenerados {regenerated} expedientes desde texto extraido.")


if __name__ == "__main__":
    main()
