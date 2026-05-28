from datetime import datetime, timezone

from app.models.text_extraction import ExtractedPageText, TextExtractionResult
from app.services.document_segmentation.document_segmenter import DocumentSegmenter


def build_text_result(pages: list[tuple[int, str]]) -> TextExtractionResult:
    return TextExtractionResult(
        expediente_id=1,
        status="extraido",
        total_pages=len(pages),
        pages=[
            ExtractedPageText(
                page_number=page_number,
                text=text,
                char_count=len(text),
            )
            for page_number, text in pages
        ],
        extracted_at=datetime.now(timezone.utc),
    )


def test_segmenter_identifies_expected_document_types() -> None:
    text_result = build_text_result(
        [
            (
                1,
                "Carta 001 solicito conformidad del servicio realizado adjunto documentos atentamente",
            ),
            (
                2,
                "Orden de servicio condiciones generales datos del proveedor monto total IGV valor",
            ),
            (
                3,
                "Recibo por honorarios electronico total honorarios retencion total neto recibido",
            ),
            (
                4,
                "Factura electronica RUC valor venta IGV importe total fecha de emision",
            ),
            (
                5,
                "Informe tecnico asunto referencia antecedentes analisis actividades realizadas conclusiones recomendaciones",
            ),
            (
                6,
                "Anexo fotografico registro fotografico evidencia fotografica imagen",
            ),
        ]
    )

    result = DocumentSegmenter().segment(text_result)

    assert result.status == "segmentado"
    assert [segment.document_type for segment in result.segments] == [
        "carta_solicitud",
        "orden_servicio",
        "recibo_honorarios",
        "factura",
        "informe_actividades",
        "anexo_fotografico",
    ]
    assert all(segment.confidence > 0 for segment in result.segments)


def test_segmenter_groups_consecutive_pages_of_same_type() -> None:
    text_result = build_text_result(
        [
            (1, "Informe asunto referencia antecedentes analisis"),
            (2, "Informe actividades realizadas conclusiones recomendaciones"),
            (3, "Factura electronica RUC IGV importe total"),
        ]
    )

    result = DocumentSegmenter().segment(text_result)

    assert len(result.segments) == 2
    assert result.segments[0].document_type == "informe_actividades"
    assert result.segments[0].page_start == 1
    assert result.segments[0].page_end == 2
    assert "actividades realizadas" in result.segments[0].text
    assert result.segments[1].document_type == "factura"


def test_segmenter_marks_low_signal_page_as_unknown() -> None:
    text_result = build_text_result([(1, "Texto general sin palabras clave administrativas")])

    result = DocumentSegmenter().segment(text_result)

    assert result.status == "sin_segmentos"
    assert result.segments[0].document_type == "desconocido"
    assert result.segments[0].confidence == 0.0


def test_segmenter_handles_paddle_ocr_order_and_receipt_variants() -> None:
    text_result = build_text_result(
        [
            (
                1,
                "umDAD E.EcuTORA wRO iDEunFicActoN ORDEN DE SERVlClO "
                "AFEC CION PRESuPuESTAL FORA DE PACO S/700.00",
            ),
            (
                2,
                "RECIBO POR lioNORARIOS ELECTRONICO Total por honorarios "
                "Rotencl6n Total Nato Roclbldo Informacl6n dol cr6dlto",
            ),
        ]
    )

    result = DocumentSegmenter().segment(text_result)

    assert [segment.document_type for segment in result.segments] == [
        "orden_servicio",
        "recibo_honorarios",
    ]


def test_segmenter_handles_strong_receipt_ocr_noise() -> None:
    text_result = build_text_result(
        [
            (
                1,
                "CUTIPA MAMANI PEDRO RECIBO POF 110NOFtARlos ELECTRONICO "
                "Total pot honoraries: 2, 500.00",
            )
        ]
    )

    result = DocumentSegmenter().segment(text_result)

    assert result.segments[0].document_type == "recibo_honorarios"


def test_segmenter_scores_logistics_order_page_without_header() -> None:
    text_result = build_text_result(
        [
            (
                1,
                "Sistema Integrado de Gestion Administrativa Modulo de Logistica "
                "UNIDAD EJECUTORA NRO IDENTIFICACION De8cripcl6n SERVICIOS DIVERSOS "
                "ORDENACION DEL SERVICIO",
            )
        ]
    )

    result = DocumentSegmenter().segment(text_result)

    assert result.segments[0].document_type == "orden_servicio"
    assert result.segments[0].confidence >= 0.35


def test_segmenter_prefers_carta_when_formal_letter_mentions_informe() -> None:
    text_result = build_text_result(
        [
            (
                1,
                "CARTA N 001-2025/MPP/GA/LAZ PARA: Gerencia de Administracion "
                "DE: LUIS ANDRADE ZAPATA ASUNTO: Primer entregable "
                "(Informe de Actividades realizadas) REFERENCIA Orden de Servicio "
                "Atentamente",
            )
        ]
    )

    result = DocumentSegmenter().segment(text_result)

    assert result.segments[0].document_type == "carta_solicitud"
    assert "estructura de carta" in result.segments[0].evidence
    assert result.segments[1].document_type == "informe_actividades"
    assert result.segments[1].page_start == 1
    assert "contenido embebido en carta" in result.segments[1].evidence


def test_segmenter_treats_acta_entrega_as_informe_and_splits_different_orders() -> None:
    text_result = build_text_result(
        [
            (
                3,
                "ACTA DE ENTREGA Se deja constancia de la entrega del servicio "
                "correspondiente a la Orden de Servicio N. 0001378 Quien entrega Quien recibe",
            ),
            (
                4,
                "Sistema Integrado de Gestion Administrativa Modulo de Logistica "
                "ORDEN DE SERVICIO N 0001378 Unidad Ejecutora Municipalidad Provincial",
            ),
            (
                5,
                "Sistema Integrado de Gestion Administrativa Modulo de Logistica "
                "ORDEN DE SERVICIO N 0000031 Unidad Ejecutora Direccion Regional Agraria",
            ),
        ]
    )

    result = DocumentSegmenter().segment(text_result)

    assert [segment.document_type for segment in result.segments] == [
        "informe_actividades",
        "orden_servicio",
        "orden_servicio",
    ]
    assert result.segments[0].page_start == 3
    assert "acta de entrega" in result.segments[0].evidence
    assert result.segments[1].page_start == 4
    assert result.segments[1].page_end == 4
    assert result.segments[2].page_start == 5
