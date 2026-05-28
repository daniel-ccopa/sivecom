import threading

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.core.config import settings
from app.schemas.document_segments import (
    DocumentSegmentationResponse,
    DocumentSegmentResponse,
)
from app.schemas.extracted_data import DataExtractionResponse, ExtractedDatumResponse
from app.schemas.expedientes import (
    ExpedienteDetailResponse,
    ExpedienteListItemResponse,
    ExpedienteUploadResponse,
)
from app.schemas.text_extraction import ExtractedPageTextResponse, TextExtractionResponse
from app.schemas.validation_result import (
    ValidationEvidenceResponse,
    ValidationItemResponse,
    ValidationRunResponse,
)
from app.services.data_extraction.extraction_repository import DataExtractionRepository
from app.services.data_extraction.field_extractor import FieldExtractor
from app.services.document_segmentation.document_segmenter import DocumentSegmenter
from app.services.document_segmentation.segmentation_repository import SegmentationRepository
from app.services.expedientes.repository import ExpedienteRepository
from app.services.pdf_processing.pdf_text_extractor import PdfTextExtractor
from app.services.pdf_processing.text_extraction_repository import TextExtractionRepository
from app.services.ocr.ocr_engine import PaddleOcrEngine
from app.services.storage.file_storage import FileStorageService
from app.services.validation.validation_engine import ValidationEngine
from app.services.validation.validation_repository import ValidationRepository

router = APIRouter()
PROCESSING_LOCK = threading.Lock()
PROCESSING_IDS_LOCK = threading.Lock()
PROCESSING_IDS: set[int] = set()


@router.get("", response_model=list[ExpedienteListItemResponse], include_in_schema=False)
@router.get("/", response_model=list[ExpedienteListItemResponse])
def list_expedientes() -> list[ExpedienteListItemResponse]:
    repository = ExpedienteRepository(settings.metadata_dir)
    return [
        build_expediente_list_item(expediente)
        for expediente in sorted(
            repository.list_all(),
            key=lambda item: item.fecha_carga,
            reverse=True,
        )
    ]


@router.post(
    "/upload",
    response_model=ExpedienteUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_expediente(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
) -> ExpedienteUploadResponse:
    storage = FileStorageService(
        upload_dir=settings.upload_dir,
        max_upload_mb=settings.max_upload_mb,
    )
    saved_file = storage.save_pdf(file)

    repository = ExpedienteRepository(settings.metadata_dir)
    expediente = repository.create_from_upload(saved_file)

    pdf_path = settings.upload_dir / saved_file.stored_filename
    mark_processing(expediente.id)
    background_tasks.add_task(process_expediente, expediente.id, pdf_path)

    return ExpedienteUploadResponse(
        id=expediente.id,
        codigo_interno=expediente.codigo_interno,
        archivo_original=expediente.archivo_original,
        tamano_bytes=expediente.tamano_bytes,
        fecha_carga=expediente.fecha_carga,
        estado=expediente.estado,
    )


@router.get("/{expediente_id}/pdf", response_class=FileResponse)
def get_pdf(expediente_id: int) -> FileResponse:
    expediente = ExpedienteRepository(settings.metadata_dir).get_by_id(expediente_id)
    if expediente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existe el expediente solicitado.",
        )

    pdf_path = settings.upload_dir / expediente.archivo_guardado
    if not pdf_path.exists() or pdf_path.suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontro el PDF almacenado.",
        )

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=expediente.archivo_original,
        headers={"Content-Disposition": "inline"},
    )


@router.post("/{expediente_id}/reprocess", response_model=ExpedienteDetailResponse)
def reprocess_expediente(
    expediente_id: int,
    background_tasks: BackgroundTasks,
) -> ExpedienteDetailResponse:
    expediente = ExpedienteRepository(settings.metadata_dir).get_by_id(expediente_id)
    if expediente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existe el expediente solicitado.",
        )

    pdf_path = settings.upload_dir / expediente.archivo_guardado
    if not pdf_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontro el PDF almacenado para reprocesar.",
        )

    mark_processing(expediente.id)
    background_tasks.add_task(process_expediente, expediente.id, pdf_path)
    summary = build_expediente_list_item(expediente)
    return ExpedienteDetailResponse(
        **summary.model_dump(),
        content_type=expediente.content_type,
    )


@router.get("/{expediente_id}", response_model=ExpedienteDetailResponse)
def get_expediente(expediente_id: int) -> ExpedienteDetailResponse:
    expediente = ExpedienteRepository(settings.metadata_dir).get_by_id(expediente_id)
    if expediente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existe el expediente solicitado.",
        )

    summary = build_expediente_list_item(expediente)
    return ExpedienteDetailResponse(
        **summary.model_dump(),
        content_type=expediente.content_type,
    )


@router.get("/{expediente_id}/texto", response_model=TextExtractionResponse)
def get_texto_extraido(expediente_id: int) -> TextExtractionResponse:
    result = TextExtractionRepository(settings.text_extraction_dir).get_by_expediente_id(
        expediente_id
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existe texto extraido para el expediente solicitado.",
        )

    return TextExtractionResponse(
        expediente_id=result.expediente_id,
        status=result.status,
        total_pages=result.total_pages,
        total_char_count=result.total_char_count,
        extracted_at=result.extracted_at,
        pages=[
            ExtractedPageTextResponse(
                page_number=page.page_number,
                text=page.text,
                char_count=page.char_count,
                extraction_method=page.extraction_method,
                ocr_used=page.ocr_used,
                ocr_confidence=page.ocr_confidence,
                error=page.error,
            )
            for page in result.pages
        ],
        error=result.error,
    )


@router.get("/{expediente_id}/segmentos", response_model=DocumentSegmentationResponse)
def get_segmentos(expediente_id: int) -> DocumentSegmentationResponse:
    result = SegmentationRepository(settings.segmentation_dir).get_by_expediente_id(
        expediente_id
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existen segmentos para el expediente solicitado.",
        )

    return DocumentSegmentationResponse(
        expediente_id=result.expediente_id,
        status=result.status,
        segmented_at=result.segmented_at,
        segments=[
            DocumentSegmentResponse(
                document_type=segment.document_type,
                page_start=segment.page_start,
                page_end=segment.page_end,
                text=segment.text,
                confidence=segment.confidence,
                evidence=segment.evidence,
            )
            for segment in result.segments
        ],
    )


@router.get("/{expediente_id}/datos", response_model=DataExtractionResponse)
def get_datos_extraidos(expediente_id: int) -> DataExtractionResponse:
    result = DataExtractionRepository(settings.data_extraction_dir).get_by_expediente_id(
        expediente_id
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existen datos extraidos para el expediente solicitado.",
        )

    return DataExtractionResponse(
        expediente_id=result.expediente_id,
        status=result.status,
        extracted_at=result.extracted_at,
        fields=[
            ExtractedDatumResponse(
                field=item.field,
                value=item.value,
                normalized_value=item.normalized_value,
                source=item.source,
                page=item.page,
                confidence=item.confidence,
                evidence=item.evidence,
                method=item.method,
            )
            for item in result.fields
        ],
    )


@router.get("/{expediente_id}/validaciones", response_model=ValidationRunResponse)
def get_validaciones(expediente_id: int) -> ValidationRunResponse:
    result = ValidationRepository(settings.validation_dir).get_by_expediente_id(
        expediente_id
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existen validaciones para el expediente solicitado.",
        )

    return ValidationRunResponse(
        expediente_id=result.expediente_id,
        verdict=result.verdict,
        summary=result.summary,
        validated_at=result.validated_at,
        validations=[
            ValidationItemResponse(
                rule_id=item.rule_id,
                tipo=item.tipo,
                resultado=item.resultado,
                severidad=item.severidad,
                mensaje=item.mensaje,
                evidencia=[
                    ValidationEvidenceResponse(
                        text=evidence.text,
                        page=evidence.page,
                        document_type=evidence.document_type,
                        field=evidence.field,
                    )
                    for evidence in item.evidencia
                ],
                recomendacion=item.recomendacion,
                passed=item.passed,
                affected_fields=item.affected_fields,
            )
            for item in result.validations
        ],
    )


@router.get("/{expediente_id}/alertas", response_model=list[ValidationItemResponse])
def get_alertas(expediente_id: int) -> list[ValidationItemResponse]:
    result = ValidationRepository(settings.validation_dir).get_by_expediente_id(
        expediente_id
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existen alertas para el expediente solicitado.",
        )

    return [
        ValidationItemResponse(
            rule_id=item.rule_id,
            tipo=item.tipo,
            resultado=item.resultado,
            severidad=item.severidad,
            mensaje=item.mensaje,
            evidencia=[
                ValidationEvidenceResponse(
                    text=evidence.text,
                    page=evidence.page,
                    document_type=evidence.document_type,
                    field=evidence.field,
                )
                for evidence in item.evidencia
            ],
            recomendacion=item.recomendacion,
            passed=item.passed,
            affected_fields=item.affected_fields,
        )
        for item in result.validations
        if item.resultado != "OK"
    ]


def build_expediente_list_item(expediente) -> ExpedienteListItemResponse:
    data_result = DataExtractionRepository(settings.data_extraction_dir).get_by_expediente_id(
        expediente.id
    )
    validation_result = ValidationRepository(settings.validation_dir).get_by_expediente_id(
        expediente.id
    )
    alert_count = (
        sum(1 for item in validation_result.validations if item.resultado != "OK")
        if validation_result is not None
        else 0
    )
    return ExpedienteListItemResponse(
        id=expediente.id,
        codigo_interno=expediente.codigo_interno,
        archivo_original=expediente.archivo_original,
        tamano_bytes=expediente.tamano_bytes,
        fecha_carga=expediente.fecha_carga,
        estado=expediente.estado,
        estado_procesamiento=processing_status(expediente.id),
        veredicto_sugerido=(
            validation_result.verdict if validation_result is not None else None
        ),
        alertas=alert_count,
        proveedor=first_field_value(data_result, "proveedor"),
        numero_orden_servicio=first_field_value(data_result, "numero_orden_servicio"),
        monto_total=(
            first_field_value(data_result, "monto_entregable")
            or first_field_value(data_result, "monto_total_os")
        ),
    )


def processing_status(expediente_id: int) -> str:
    with PROCESSING_IDS_LOCK:
        if expediente_id in PROCESSING_IDS:
            return "procesando"
    if ValidationRepository(settings.validation_dir).get_by_expediente_id(expediente_id):
        return "procesado"
    if DataExtractionRepository(settings.data_extraction_dir).get_by_expediente_id(expediente_id):
        return "datos_extraidos"
    if SegmentationRepository(settings.segmentation_dir).get_by_expediente_id(expediente_id):
        return "segmentado"
    if TextExtractionRepository(settings.text_extraction_dir).get_by_expediente_id(expediente_id):
        return "texto_extraido"
    return "pendiente"


def first_field_value(data_result, field_name: str) -> str | None:
    if data_result is None:
        return None
    for item in data_result.fields:
        if item.field == field_name:
            if field_name in {
                "proveedor",
                "concepto",
                "descripcion_servicio",
            }:
                return item.value
            return item.normalized_value or item.value
    return None


def mark_processing(expediente_id: int) -> None:
    with PROCESSING_IDS_LOCK:
        PROCESSING_IDS.add(expediente_id)


def unmark_processing(expediente_id: int) -> None:
    with PROCESSING_IDS_LOCK:
        PROCESSING_IDS.discard(expediente_id)


def process_expediente(expediente_id: int, pdf_path) -> None:
    try:
        with PROCESSING_LOCK:
            extraction_result = PdfTextExtractor(
                ocr_engine=PaddleOcrEngine(
                    language=settings.ocr_language,
                    model_base_dir=settings.paddle_ocr_base_dir,
                    use_gpu=settings.paddle_use_gpu,
                    use_textline_orientation=settings.paddle_use_textline_orientation,
                ),
                ocr_dpi=settings.ocr_dpi,
            ).extract(
                expediente_id=expediente_id,
                pdf_path=pdf_path,
            )
            TextExtractionRepository(settings.text_extraction_dir).save(extraction_result)

            segmentation_result = DocumentSegmenter().segment(extraction_result)
            SegmentationRepository(settings.segmentation_dir).save(segmentation_result)

            data_repository = DataExtractionRepository(settings.data_extraction_dir)
            data_extraction_result = FieldExtractor().extract(segmentation_result)
            data_repository.save(data_extraction_result)

            validation_result = ValidationEngine().evaluate(
                segmentation=segmentation_result,
                extraction=data_extraction_result,
                previous_extractions=data_repository.list_all(
                    exclude_expediente_id=expediente_id
                ),
            )
            ValidationRepository(settings.validation_dir).save(validation_result)
    finally:
        unmark_processing(expediente_id)
