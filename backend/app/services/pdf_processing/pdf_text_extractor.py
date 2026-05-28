from datetime import datetime, timezone
from pathlib import Path

import fitz

from app.models.text_extraction import ExtractedPageText, TextExtractionResult
from app.services.ocr.ocr_engine import OcrEngine, OcrUnavailableError, PaddleOcrEngine


class PdfTextExtractor:
    """Extract text from PDF pages, using OCR only when direct text is absent."""

    def __init__(
        self,
        ocr_engine: OcrEngine | None = None,
        ocr_dpi: int = 200,
    ) -> None:
        self.ocr_engine = ocr_engine or PaddleOcrEngine()
        self.ocr_dpi = ocr_dpi

    def extract(self, expediente_id: int, pdf_path: Path) -> TextExtractionResult:
        try:
            with fitz.open(str(pdf_path)) as document:
                pages = [
                    self._extract_page_text(page_number=index + 1, page=page)
                    for index, page in enumerate(document)
                ]
        except Exception:
            return TextExtractionResult(
                expediente_id=expediente_id,
                status="error_extraccion",
                total_pages=0,
                pages=[],
                extracted_at=datetime.now(timezone.utc),
                error="No se pudo abrir o leer el PDF para extraer texto.",
            )

        status = self._resolve_status(pages)
        error = self._resolve_result_error(status)

        return TextExtractionResult(
            expediente_id=expediente_id,
            status=status,
            total_pages=len(pages),
            pages=pages,
            extracted_at=datetime.now(timezone.utc),
            error=error,
        )

    def _extract_page_text(self, page_number: int, page: fitz.Page) -> ExtractedPageText:
        text = page.get_text("text").strip()
        if text:
            return ExtractedPageText(
                page_number=page_number,
                text=text,
                char_count=len(text),
                extraction_method="direct_text",
                ocr_used=False,
            )

        return self._extract_ocr_page_text(page_number=page_number, page=page)

    def _extract_ocr_page_text(self, page_number: int, page: fitz.Page) -> ExtractedPageText:
        try:
            image_bytes = self._render_page_to_png(page)
            ocr_result = self.ocr_engine.extract_text(image_bytes)
        except OcrUnavailableError as exc:
            return ExtractedPageText(
                page_number=page_number,
                text="",
                char_count=0,
                extraction_method="ocr",
                ocr_used=True,
                error=str(exc),
            )
        except Exception:
            return ExtractedPageText(
                page_number=page_number,
                text="",
                char_count=0,
                extraction_method="ocr",
                ocr_used=True,
                error="No se pudo convertir la pagina a imagen o aplicar OCR.",
            )

        ocr_text = ocr_result.text.strip()
        page_error = None
        if not ocr_text:
            page_error = "OCR ejecutado sin texto detectado en la pagina."

        return ExtractedPageText(
            page_number=page_number,
            text=ocr_text,
            char_count=len(ocr_text),
            extraction_method="ocr",
            ocr_used=True,
            ocr_confidence=ocr_result.confidence,
            error=page_error,
        )

    def _render_page_to_png(self, page: fitz.Page) -> bytes:
        zoom = self.ocr_dpi / 72
        matrix = fitz.Matrix(zoom, zoom)
        pixmap = page.get_pixmap(matrix=matrix, alpha=False)
        return pixmap.tobytes("png")

    @staticmethod
    def _resolve_status(pages: list[ExtractedPageText]) -> str:
        has_text = any(page.text.strip() for page in pages)
        has_ocr_text = any(page.ocr_used and page.text.strip() for page in pages)
        has_processing_errors = any(
            page.error and page.error != "OCR ejecutado sin texto detectado en la pagina."
            for page in pages
        )
        if has_text and has_processing_errors:
            return "extraido_parcial"
        if has_ocr_text:
            return "extraido_con_ocr"
        if has_text:
            return "extraido"
        if has_processing_errors:
            return "error_ocr"
        return "sin_texto_extraible"

    @staticmethod
    def _resolve_result_error(status: str) -> str | None:
        if status == "sin_texto_extraible":
            return "No se encontro texto extraible en el PDF."
        if status == "error_ocr":
            return "No se pudo extraer texto de las paginas sin texto digital."
        if status == "extraido_parcial":
            return "Algunas paginas fueron extraidas y otras requieren revision."
        return None
