import json

import fitz
from fastapi.testclient import TestClient

from app.api import routes_expedientes
from app.core.config import settings
from app.main import create_app
from app.services.ocr.ocr_engine import OcrResult


class FakeOcrEngine:
    def __init__(self, language: str = "es", **_: object) -> None:
        self.language = language

    def extract_text(self, image_bytes: bytes) -> OcrResult:
        return OcrResult(text="Texto OCR desde endpoint", confidence=86.0)


def make_pdf_bytes(text: str | None = None) -> bytes:
    document = fitz.open()
    page = document.new_page()
    if text:
        page.insert_text((72, 72), text)
    payload = document.tobytes()
    document.close()
    return payload


def test_upload_valid_pdf_saves_file_and_metadata(monkeypatch, tmp_path) -> None:
    upload_dir = tmp_path / "uploads"
    metadata_dir = tmp_path / "metadata"
    text_extraction_dir = tmp_path / "text_extractions"
    segmentation_dir = tmp_path / "segmentations"
    data_extraction_dir = tmp_path / "data_extractions"
    validation_dir = tmp_path / "validations"
    monkeypatch.setattr(settings, "upload_dir", upload_dir)
    monkeypatch.setattr(settings, "metadata_dir", metadata_dir)
    monkeypatch.setattr(settings, "text_extraction_dir", text_extraction_dir)
    monkeypatch.setattr(settings, "segmentation_dir", segmentation_dir)
    monkeypatch.setattr(settings, "data_extraction_dir", data_extraction_dir)
    monkeypatch.setattr(settings, "validation_dir", validation_dir)

    client = TestClient(create_app())
    response = client.post(
        "/expedientes/upload",
        files={
            "file": (
                "expediente.pdf",
                make_pdf_bytes("Texto digital de prueba"),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["archivo_original"] == "expediente.pdf"
    assert payload["estado"] == "pendiente"
    assert payload["tamano_bytes"] > 0
    assert payload["codigo_interno"] == "SIV-000001"

    saved_files = list(upload_dir.glob("*.pdf"))
    assert len(saved_files) == 1

    metadata_file = metadata_dir / "expedientes.json"
    metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
    assert metadata[0]["archivo_original"] == "expediente.pdf"
    assert metadata[0]["estado"] == "pendiente"

    extraction_file = text_extraction_dir / "expediente_000001.json"
    extraction = json.loads(extraction_file.read_text(encoding="utf-8"))
    assert extraction["status"] == "extraido"
    assert extraction["pages"][0]["text"] == "Texto digital de prueba"
    assert extraction["pages"][0]["extraction_method"] == "direct_text"
    assert extraction["pages"][0]["ocr_used"] is False

    segmentation_file = segmentation_dir / "expediente_000001.json"
    segmentation = json.loads(segmentation_file.read_text(encoding="utf-8"))
    assert segmentation["expediente_id"] == 1
    assert segmentation["segments"][0]["document_type"] == "desconocido"

    data_extraction_file = data_extraction_dir / "expediente_000001.json"
    data_extraction = json.loads(data_extraction_file.read_text(encoding="utf-8"))
    assert data_extraction["expediente_id"] == 1
    assert data_extraction["status"] == "sin_datos_extraidos"

    validation_file = validation_dir / "expediente_000001.json"
    validation = json.loads(validation_file.read_text(encoding="utf-8"))
    assert validation["expediente_id"] == 1
    assert validation["verdict"] == "rechazar"
    assert validation["validations"][0]["tipo"] == "documentos_obligatorios"

    list_response = client.get("/expedientes")
    assert list_response.status_code == 200
    assert list_response.json()[0]["codigo_interno"] == "SIV-000001"
    assert list_response.json()[0]["estado_procesamiento"] == "procesado"
    assert list_response.json()[0]["veredicto_sugerido"] == "rechazar"

    detail_response = client.get("/expedientes/1")
    assert detail_response.status_code == 200
    assert detail_response.json()["archivo_original"] == "expediente.pdf"

    pdf_response = client.get("/expedientes/1/pdf")
    assert pdf_response.status_code == 200
    assert pdf_response.headers["content-type"] == "application/pdf"

    alert_response = client.get("/expedientes/1/alertas")
    assert alert_response.status_code == 200
    assert len(alert_response.json()) > 0


def test_upload_invalid_file_is_rejected(monkeypatch, tmp_path) -> None:
    upload_dir = tmp_path / "uploads"
    metadata_dir = tmp_path / "metadata"
    text_extraction_dir = tmp_path / "text_extractions"
    segmentation_dir = tmp_path / "segmentations"
    data_extraction_dir = tmp_path / "data_extractions"
    validation_dir = tmp_path / "validations"
    monkeypatch.setattr(settings, "upload_dir", upload_dir)
    monkeypatch.setattr(settings, "metadata_dir", metadata_dir)
    monkeypatch.setattr(settings, "text_extraction_dir", text_extraction_dir)
    monkeypatch.setattr(settings, "segmentation_dir", segmentation_dir)
    monkeypatch.setattr(settings, "data_extraction_dir", data_extraction_dir)
    monkeypatch.setattr(settings, "validation_dir", validation_dir)

    client = TestClient(create_app())
    response = client.post(
        "/expedientes/upload",
        files={"file": ("nota.txt", b"contenido no pdf", "text/plain")},
    )

    assert response.status_code == 400
    assert not upload_dir.exists()
    assert not metadata_dir.exists()
    assert not text_extraction_dir.exists()
    assert not segmentation_dir.exists()
    assert not data_extraction_dir.exists()
    assert not validation_dir.exists()


def test_get_texto_extraido_returns_pages(monkeypatch, tmp_path) -> None:
    upload_dir = tmp_path / "uploads"
    metadata_dir = tmp_path / "metadata"
    text_extraction_dir = tmp_path / "text_extractions"
    segmentation_dir = tmp_path / "segmentations"
    data_extraction_dir = tmp_path / "data_extractions"
    validation_dir = tmp_path / "validations"
    monkeypatch.setattr(settings, "upload_dir", upload_dir)
    monkeypatch.setattr(settings, "metadata_dir", metadata_dir)
    monkeypatch.setattr(settings, "text_extraction_dir", text_extraction_dir)
    monkeypatch.setattr(settings, "segmentation_dir", segmentation_dir)
    monkeypatch.setattr(settings, "data_extraction_dir", data_extraction_dir)
    monkeypatch.setattr(settings, "validation_dir", validation_dir)

    client = TestClient(create_app())
    upload_response = client.post(
        "/expedientes/upload",
        files={
            "file": (
                "expediente.pdf",
                make_pdf_bytes("Informe asunto referencia antecedentes analisis"),
                "application/pdf",
            )
        },
    )

    expediente_id = upload_response.json()["id"]
    response = client.get(f"/expedientes/{expediente_id}/texto")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "extraido"
    assert payload["total_pages"] == 1
    assert payload["total_char_count"] > 0
    assert payload["pages"][0]["text"] == "Informe asunto referencia antecedentes analisis"
    assert payload["pages"][0]["extraction_method"] == "direct_text"
    assert payload["pages"][0]["ocr_used"] is False

    segment_response = client.get(f"/expedientes/{expediente_id}/segmentos")
    assert segment_response.status_code == 200
    assert segment_response.json()["segments"][0]["document_type"] == "informe_actividades"

    data_response = client.get(f"/expedientes/{expediente_id}/datos")
    assert data_response.status_code == 200
    assert data_response.json()["expediente_id"] == expediente_id

    validation_response = client.get(f"/expedientes/{expediente_id}/validaciones")
    assert validation_response.status_code == 200
    assert validation_response.json()["expediente_id"] == expediente_id
    assert "verdict" in validation_response.json()


def test_upload_scanned_pdf_uses_mocked_ocr(monkeypatch, tmp_path) -> None:
    upload_dir = tmp_path / "uploads"
    metadata_dir = tmp_path / "metadata"
    text_extraction_dir = tmp_path / "text_extractions"
    segmentation_dir = tmp_path / "segmentations"
    data_extraction_dir = tmp_path / "data_extractions"
    validation_dir = tmp_path / "validations"
    monkeypatch.setattr(settings, "upload_dir", upload_dir)
    monkeypatch.setattr(settings, "metadata_dir", metadata_dir)
    monkeypatch.setattr(settings, "text_extraction_dir", text_extraction_dir)
    monkeypatch.setattr(settings, "segmentation_dir", segmentation_dir)
    monkeypatch.setattr(settings, "data_extraction_dir", data_extraction_dir)
    monkeypatch.setattr(settings, "validation_dir", validation_dir)
    monkeypatch.setattr(routes_expedientes, "PaddleOcrEngine", FakeOcrEngine)

    client = TestClient(create_app())
    upload_response = client.post(
        "/expedientes/upload",
        files={
            "file": (
                "escaneado.pdf",
                make_pdf_bytes(),
                "application/pdf",
            )
        },
    )

    expediente_id = upload_response.json()["id"]
    response = client.get(f"/expedientes/{expediente_id}/texto")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "extraido_con_ocr"
    assert payload["pages"][0]["text"] == "Texto OCR desde endpoint"
    assert payload["pages"][0]["extraction_method"] == "ocr"
    assert payload["pages"][0]["ocr_used"] is True
    assert payload["pages"][0]["ocr_confidence"] == 86.0
