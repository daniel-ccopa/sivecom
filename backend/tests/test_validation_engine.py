from datetime import datetime, timezone

from app.models.document_segment import DocumentSegment, DocumentSegmentationResult
from app.models.extracted_data import DataExtractionResult, ExtractedDatum
from app.services.validation.validation_engine import ValidationEngine


def build_segmentation(segments: list[DocumentSegment]) -> DocumentSegmentationResult:
    return DocumentSegmentationResult(
        expediente_id=1,
        status="segmentado",
        segments=segments,
        segmented_at=datetime.now(timezone.utc),
    )


def build_extraction(fields: list[ExtractedDatum]) -> DataExtractionResult:
    return DataExtractionResult(
        expediente_id=1,
        status="extraido",
        fields=fields,
        extracted_at=datetime.now(timezone.utc),
    )


def segment(document_type: str, page: int, text: str) -> DocumentSegment:
    return DocumentSegment(
        document_type=document_type,
        page_start=page,
        page_end=page,
        text=text,
        confidence=0.85,
        evidence=[document_type],
    )


def datum(field: str, value: str, normalized_value: str, source: str, page: int) -> ExtractedDatum:
    return ExtractedDatum(
        field=field,
        value=value,
        normalized_value=normalized_value,
        source=source,
        page=page,
        confidence=0.9,
        evidence=f"{field}: {value}",
    )


def by_rule(result, rule_id: str):
    return next(item for item in result.validations if item.rule_id == rule_id)


def core_fields() -> list[ExtractedDatum]:
    return [
        datum("numero_orden_servicio", "0001582", "0001582", "orden_servicio", 2),
        datum("numero_orden_servicio", "0001582", "0001582", "recibo_honorarios", 9),
        datum("ruc", "20481234567", "20481234567", "orden_servicio", 2),
        datum("ruc", "20481234567", "20481234567", "recibo_honorarios", 9),
        datum("proveedor", "SERVICIOS MUNICIPALES SAC", "servicios municipales sac", "orden_servicio", 2),
        datum("monto_total_os", "3000.00", "3000.00", "orden_servicio", 2),
        datum("monto_entregable", "1500.00", "1500.00", "recibo_honorarios", 9),
        datum("concepto", "Servicio tecnico", "servicio tecnico", "orden_servicio", 2),
        datum("concepto", "Servicio tecnico de mantenimiento", "servicio tecnico de mantenimiento", "recibo_honorarios", 9),
        datum(
            "descripcion_servicio",
            "Servicio de mantenimiento de computadoras",
            "servicio de mantenimiento de computadoras",
            "orden_servicio",
            2,
        ),
    ]


def test_validation_engine_passes_core_fields() -> None:
    result = ValidationEngine().evaluate(
        segmentation=build_segmentation(
            [
                segment("carta_solicitud", 1, "Carta de solicitud"),
                segment("orden_servicio", 2, "Orden de servicio"),
                segment("recibo_honorarios", 9, "Recibo"),
                segment("informe_actividades", 4, "Actividades"),
            ]
        ),
        extraction=build_extraction(core_fields()),
    )

    assert result.verdict == "procede_conformidad"
    assert result.summary == {"ok": 9, "advertencias": 0, "errores": 0, "criticas": 0}
    assert by_rule(result, "R000").resultado == "OK"
    assert by_rule(result, "R001").resultado == "OK"
    assert by_rule(result, "R004").resultado == "OK"


def test_validation_engine_warns_for_missing_noncritical_core_fields() -> None:
    fields = [
        datum("numero_orden_servicio", "0001582", "0001582", "orden_servicio", 2),
        datum("ruc", "20481234567", "20481234567", "orden_servicio", 2),
    ]

    result = ValidationEngine().evaluate(
        segmentation=build_segmentation(
            [
                segment("carta_solicitud", 1, "Carta"),
                segment("orden_servicio", 2, "Orden"),
                segment("recibo_honorarios", 3, "Recibo"),
                segment("informe_actividades", 4, "Informe"),
            ]
        ),
        extraction=build_extraction(fields),
    )

    assert result.verdict == "revision_manual"
    assert by_rule(result, "R001").resultado == "ADVERTENCIA"
    assert "Faltan campos principales" in by_rule(result, "R001").mensaje


def test_validation_engine_rejects_only_when_deliverable_exceeds_order_amount() -> None:
    fields = [
        *core_fields(),
        datum("monto_entregable", "3500.00", "3500.00", "factura", 9),
    ]

    result = ValidationEngine().evaluate(
        segmentation=build_segmentation(
            [
                segment("carta_solicitud", 1, "Carta"),
                segment("orden_servicio", 2, "Orden"),
                segment("recibo_honorarios", 3, "Recibo"),
                segment("informe_actividades", 4, "Informe"),
            ]
        ),
        extraction=build_extraction(fields),
    )

    assert result.verdict == "rechazar"
    assert by_rule(result, "R004").resultado == "ERROR"


def test_validation_engine_warns_for_ruc_conflict_without_rejecting() -> None:
    fields = [
        *core_fields(),
        datum("ruc", "20111111111", "20111111111", "factura", 9),
    ]

    result = ValidationEngine().evaluate(
        segmentation=build_segmentation(
            [
                segment("carta_solicitud", 1, "Carta"),
                segment("orden_servicio", 2, "Orden"),
                segment("recibo_honorarios", 3, "Recibo"),
                segment("informe_actividades", 4, "Informe"),
            ]
        ),
        extraction=build_extraction(fields),
    )

    assert result.verdict == "revision_manual"
    assert by_rule(result, "R003").resultado == "ADVERTENCIA"


def test_validation_engine_errors_when_required_document_is_missing() -> None:
    result = ValidationEngine().evaluate(
        segmentation=build_segmentation(
            [
                segment("carta_solicitud", 1, "Carta"),
                segment("orden_servicio", 2, "Orden"),
                segment("informe_actividades", 4, "Informe"),
            ]
        ),
        extraction=build_extraction(core_fields()),
    )

    assert result.verdict == "rechazar"
    assert by_rule(result, "R000").resultado == "ERROR"
    assert "comprobante de pago" in by_rule(result, "R000").mensaje


def test_validation_engine_accepts_invoice_as_payment_document() -> None:
    result = ValidationEngine().evaluate(
        segmentation=build_segmentation(
            [
                segment("carta_solicitud", 1, "Carta"),
                segment("orden_servicio", 2, "Orden"),
                segment("factura", 3, "Factura"),
                segment("informe_actividades", 4, "Informe"),
            ]
        ),
        extraction=build_extraction(core_fields()),
    )

    assert by_rule(result, "R000").resultado == "OK"


def test_validation_engine_ignores_delivery_label_when_comparing_service_text() -> None:
    fields = [
        *core_fields(),
        datum(
            "concepto",
            "PRIMER ENTREGABLE (Informe de Actividades realizadas)",
            "primer entregable informe de actividades realizadas",
            "carta_solicitud",
            1,
        ),
        datum(
            "concepto",
            "SERVICIO COMO APOYO TECNICO ESPECIALIZADO EN CONTRATACIONES PUBLICAS",
            "servicio como apoyo tecnico especializado en contrataciones publicas",
            "orden_servicio",
            2,
        ),
        datum(
            "concepto",
            "SERVICIO DE APOYO TECNICO ESPECIALIZADO EN CONTRATACIONES PUBLICAS",
            "servicio de apoyo tecnico especializado en contrataciones publicas",
            "recibo_honorarios",
            9,
        ),
    ]

    result = ValidationEngine().evaluate(
        segmentation=build_segmentation(
            [
                segment("carta_solicitud", 1, "Carta"),
                segment("orden_servicio", 2, "Orden"),
                segment("recibo_honorarios", 3, "Recibo"),
                segment("informe_actividades", 4, "Informe"),
            ]
        ),
        extraction=build_extraction(fields),
    )

    assert by_rule(result, "R007").resultado == "OK"


def test_validation_engine_ignores_conformity_request_as_service_text() -> None:
    fields = [
        *core_fields(),
        datum(
            "concepto",
            "SOLICITO CONFORMIDAD DE PAGO AL PRIMER ENTREGABLE",
            "solicito conformidad de pago al primer entregable",
            "carta_solicitud",
            1,
        ),
        datum(
            "concepto",
            "SERVICIO DE RESPONSABLE TECNICO PARA OBRAS PUBLICAS",
            "servicio de responsable tecnico para obras publicas",
            "orden_servicio",
            2,
        ),
        datum(
            "concepto",
            "SERVICIO DE RESPONSABLE TECNICO PARA OBRAS PUBLICAS",
            "servicio de responsable tecnico para obras publicas",
            "recibo_honorarios",
            9,
        ),
    ]

    result = ValidationEngine().evaluate(
        segmentation=build_segmentation(
            [
                segment("carta_solicitud", 1, "Carta"),
                segment("orden_servicio", 2, "Orden"),
                segment("recibo_honorarios", 3, "Recibo"),
                segment("informe_actividades", 4, "Informe"),
            ]
        ),
        extraction=build_extraction(fields),
    )

    assert by_rule(result, "R007").resultado == "OK"


def test_validation_engine_ignores_conformity_processing_phrase_as_service_text() -> None:
    fields = [
        datum("numero_orden_servicio", "0001378", "0001378", "orden_servicio", 2),
        datum("ruc", "10012640892", "10012640892", "orden_servicio", 2),
        datum("proveedor", "GONZALES VALERO GUIDO", "gonzales valero guido", "orden_servicio", 2),
        datum("monto_total_os", "2000.00", "2000.00", "orden_servicio", 2),
        datum("monto_entregable", "2000.00", "2000.00", "factura", 3),
        datum(
            "concepto",
            "Tramite de conformidad para el pago correspondiente.",
            "tramite de conformidad para el pago correspondiente.",
            "carta_solicitud",
            1,
        ),
        datum(
            "concepto",
            "SERVICIO DE DISENO IMPRESION Y EMPASTADO",
            "servicio de diseno impresion y empastado",
            "orden_servicio",
            2,
        ),
        datum(
            "concepto",
            "SERVICIO DE DISENO, IMPRESIO Y EMPASTADO",
            "servicio de diseno impresio y empastado",
            "factura",
            3,
        ),
        datum(
            "descripcion_servicio",
            "SERVICIO DE DISENO IMPRESION Y EMPASTADO",
            "servicio de diseno impresion y empastado",
            "orden_servicio",
            2,
        ),
    ]

    result = ValidationEngine().evaluate(
        segmentation=build_segmentation(
            [
                segment("carta_solicitud", 1, "Carta"),
                segment("orden_servicio", 2, "Orden"),
                segment("factura", 3, "Factura"),
                segment("informe_actividades", 4, "Acta de entrega"),
            ]
        ),
        extraction=build_extraction(fields),
    )

    assert by_rule(result, "R007").resultado == "OK"


def test_validation_engine_accepts_provider_name_in_different_order() -> None:
    base_fields = [field for field in core_fields() if field.field != "proveedor"]
    fields = [
        *base_fields,
        datum("proveedor", "PEDRO CUTIPA MAMANI", "pedro cutipa mamani", "carta_solicitud", 1),
        datum("proveedor", "CUTIPA MAMANI PEDRO", "cutipa mamani pedro", "recibo_honorarios", 4),
    ]

    result = ValidationEngine().evaluate(
        segmentation=build_segmentation(
            [
                segment("carta_solicitud", 1, "Carta"),
                segment("orden_servicio", 2, "Orden"),
                segment("recibo_honorarios", 4, "Recibo"),
                segment("informe_actividades", 6, "Informe"),
            ]
        ),
        extraction=build_extraction(fields),
    )

    assert by_rule(result, "R006").resultado == "OK"


def test_validation_engine_accepts_common_ocr_variants_in_service_text() -> None:
    fields = [
        datum("numero_orden_servicio", "0004", "0004", "carta_solicitud", 1),
        datum("ruc", "10416669517", "10416669517", "recibo_honorarios", 4),
        datum("proveedor", "PEDRO CUTIPA MAMANI", "pedro cutipa mamani", "carta_solicitud", 1),
        datum("proveedor", "CUTIPA MAMANI PEDRO", "cutipa mamani pedro", "recibo_honorarios", 4),
        datum("monto_total_os", "2500.00", "2500.00", "orden_servicio", 2),
        datum("monto_entregable", "2500.00", "2500.00", "recibo_honorarios", 4),
        datum(
            "concepto",
            "sERvlclct DE REspONSABm TECNlco PARA IA SUB GERENCIA DE OBRAS PUBLICAS",
            "servlclct de responsabm tecnlco para ia sub gerencia de obras publicas",
            "orden_servicio",
            2,
        ),
        datum(
            "descripcion_servicio",
            "SERVICIO DE RESPONSABLE TECNICO PARA LA SUB GERENCIA DE OBRAS PUBLICAS",
            "servicio de responsable tecnico para la sub gerencia de obras publicas",
            "recibo_honorarios",
            4,
        ),
    ]

    result = ValidationEngine().evaluate(
        segmentation=build_segmentation(
            [
                segment("carta_solicitud", 1, "Carta"),
                segment("orden_servicio", 2, "Orden"),
                segment("recibo_honorarios", 4, "Recibo"),
                segment("informe_actividades", 6, "Informe"),
            ]
        ),
        extraction=build_extraction(fields),
    )

    assert by_rule(result, "R007").resultado == "OK"


def test_validation_engine_accepts_order_service_numbers_with_different_zero_padding() -> None:
    fields = [
        field
        for field in core_fields()
        if field.field != "numero_orden_servicio"
    ]
    fields.extend(
        [
            datum("numero_orden_servicio", "001089", "001089", "carta_solicitud", 1),
            datum("numero_orden_servicio", "0001089", "0001089", "orden_servicio", 4),
        ]
    )

    result = ValidationEngine().evaluate(
        segmentation=build_segmentation(
            [
                segment("carta_solicitud", 1, "Carta"),
                segment("orden_servicio", 4, "Orden"),
                segment("recibo_honorarios", 6, "Recibo"),
                segment("informe_actividades", 3, "Informe"),
            ]
        ),
        extraction=build_extraction(fields),
    )

    assert by_rule(result, "R002").resultado == "OK"


def test_validation_engine_accepts_service_text_only_from_order_when_required_documents_exist() -> None:
    fields = [
        field
        for field in core_fields()
        if field.field not in {"concepto", "descripcion_servicio"}
    ]
    fields.extend(
        [
            datum(
                "concepto",
                "SERVICIO DE APOYO ADMINISTRATIVO",
                "servicio de apoyo administrativo",
                "orden_servicio",
                4,
            ),
            datum(
                "descripcion_servicio",
                "SERVICIO DE APOYO ADMINISTRATIVO",
                "servicio de apoyo administrativo",
                "orden_servicio",
                4,
            ),
        ]
    )

    result = ValidationEngine().evaluate(
        segmentation=build_segmentation(
            [
                segment("carta_solicitud", 1, "Carta"),
                segment("orden_servicio", 4, "Orden"),
                segment("recibo_honorarios", 6, "Recibo"),
                segment("informe_actividades", 3, "Informe"),
            ]
        ),
        extraction=build_extraction(fields),
    )

    assert by_rule(result, "R007").resultado == "OK"


def test_validation_engine_accepts_deliverable_amount_matching_schedule() -> None:
    fields = [
        field
        for field in core_fields()
        if field.field not in {"monto_total_os", "monto_entregable"}
    ]
    fields.extend(
        [
            datum("monto_total_os", "5000.00", "5000.00", "orden_servicio", 2),
            datum("monto_entregable", "2500.00", "2500.00", "recibo_honorarios", 4),
            datum("numero_entregables", "2 entregables", "2", "orden_servicio", 2),
            datum("porcentaje_entregable", "Entregable 1: 50%", "1:50", "orden_servicio", 2),
            datum("porcentaje_entregable", "Entregable 2: 50%", "2:50", "orden_servicio", 2),
        ]
    )

    result = ValidationEngine().evaluate(
        segmentation=build_segmentation(
            [
                segment("carta_solicitud", 1, "Carta"),
                segment("orden_servicio", 2, "Orden"),
                segment("recibo_honorarios", 4, "Recibo"),
                segment("informe_actividades", 6, "Informe"),
            ]
        ),
        extraction=build_extraction(fields),
    )

    assert by_rule(result, "R008").resultado == "OK"


def test_validation_engine_warns_when_deliverable_amount_does_not_match_schedule() -> None:
    fields = [
        field
        for field in core_fields()
        if field.field not in {"monto_total_os", "monto_entregable"}
    ]
    fields.extend(
        [
            datum("monto_total_os", "5000.00", "5000.00", "orden_servicio", 2),
            datum("monto_entregable", "3000.00", "3000.00", "recibo_honorarios", 4),
            datum("numero_entregables", "2 entregables", "2", "orden_servicio", 2),
            datum("porcentaje_entregable", "Entregable 1: 50%", "1:50", "orden_servicio", 2),
            datum("porcentaje_entregable", "Entregable 2: 50%", "2:50", "orden_servicio", 2),
        ]
    )

    result = ValidationEngine().evaluate(
        segmentation=build_segmentation(
            [
                segment("carta_solicitud", 1, "Carta"),
                segment("orden_servicio", 2, "Orden"),
                segment("recibo_honorarios", 4, "Recibo"),
                segment("informe_actividades", 6, "Informe"),
            ]
        ),
        extraction=build_extraction(fields),
    )

    assert by_rule(result, "R008").resultado == "ADVERTENCIA"
