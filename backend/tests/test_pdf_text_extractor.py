import fitz

from app.services.ocr.ocr_engine import OcrResult, OcrUnavailableError
from app.services.pdf_processing.pdf_text_extractor import PdfTextExtractor


class FakeOcrEngine:
    def __init__(self, text: str, confidence: float | None = 88.5) -> None:
        self.text = text
        self.confidence = confidence
        self.calls = 0

    def extract_text(self, image_bytes: bytes) -> OcrResult:
        self.calls += 1
        assert image_bytes.startswith(b"\x89PNG")
        return OcrResult(text=self.text, confidence=self.confidence)


class FailingOcrEngine:
    def extract_text(self, image_bytes: bytes) -> OcrResult:
        raise OcrUnavailableError("OCR no disponible en prueba.")


def make_pdf(path, text: str | None = None) -> None:
    document = fitz.open()
    page = document.new_page()
    if text:
        page.insert_text((72, 72), text)
    document.save(path)
    document.close()


def test_pdf_text_extractor_extracts_text_by_page(tmp_path) -> None:
    pdf_path = tmp_path / "digital.pdf"
    make_pdf(pdf_path, "Orden de servicio digital")
    ocr_engine = FakeOcrEngine("No deberia usarse")

    result = PdfTextExtractor(ocr_engine=ocr_engine).extract(expediente_id=1, pdf_path=pdf_path)

    assert result.status == "extraido"
    assert result.total_pages == 1
    assert result.pages[0].page_number == 1
    assert result.pages[0].text == "Orden de servicio digital"
    assert result.pages[0].extraction_method == "direct_text"
    assert result.pages[0].ocr_used is False
    assert ocr_engine.calls == 0


def test_pdf_text_extractor_uses_ocr_when_page_has_no_text(tmp_path) -> None:
    pdf_path = tmp_path / "sin_texto.pdf"
    make_pdf(pdf_path)
    ocr_engine = FakeOcrEngine("Texto detectado por OCR", confidence=91.0)

    result = PdfTextExtractor(ocr_engine=ocr_engine).extract(expediente_id=1, pdf_path=pdf_path)

    assert result.status == "extraido_con_ocr"
    assert result.total_pages == 1
    assert result.pages[0].text == "Texto detectado por OCR"
    assert result.pages[0].extraction_method == "ocr"
    assert result.pages[0].ocr_used is True
    assert result.pages[0].ocr_confidence == 91.0
    assert result.pages[0].error is None
    assert ocr_engine.calls == 1


def test_pdf_text_extractor_marks_empty_ocr_result(tmp_path) -> None:
    pdf_path = tmp_path / "sin_texto.pdf"
    make_pdf(pdf_path)
    ocr_engine = FakeOcrEngine("", confidence=None)

    result = PdfTextExtractor(ocr_engine=ocr_engine).extract(expediente_id=1, pdf_path=pdf_path)

    assert result.status == "sin_texto_extraible"
    assert result.total_pages == 1
    assert result.total_char_count == 0
    assert result.pages[0].extraction_method == "ocr"
    assert result.pages[0].ocr_used is True
    assert result.pages[0].error == "OCR ejecutado sin texto detectado en la pagina."
    assert result.error is not None


def test_pdf_text_extractor_handles_ocr_unavailable(tmp_path) -> None:
    pdf_path = tmp_path / "sin_ocr.pdf"
    make_pdf(pdf_path)

    result = PdfTextExtractor(ocr_engine=FailingOcrEngine()).extract(
        expediente_id=1,
        pdf_path=pdf_path,
    )

    assert result.status == "error_ocr"
    assert result.pages[0].ocr_used is True
    assert result.pages[0].error == "OCR no disponible en prueba."
