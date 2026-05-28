from datetime import datetime, timezone

from app.models.document_segment import DocumentSegment, DocumentSegmentationResult
from app.services.data_extraction.field_extractor import FieldExtractor


def build_segmentation(segments: list[DocumentSegment]) -> DocumentSegmentationResult:
    return DocumentSegmentationResult(
        expediente_id=1,
        status="segmentado",
        segments=segments,
        segmented_at=datetime.now(timezone.utc),
    )


def by_field(result, field: str):
    return [item for item in result.fields if item.field == field]


def test_field_extractor_extracts_key_data_from_segments() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="orden_servicio",
                page_start=2,
                page_end=2,
                text=(
                    "ORDEN DE SERVICIO N 0001582\n"
                    "Raz\u00f3n Social: SERVICIOS MUNICIPALES DEL SUR SAC\n"
                    "RUC: 20481234567\n"
                    "\u00c1rea solicitante: Subgerencia de Informatica\n"
                    "Concepto: Servicio tecnico\n"
                    "Descripci\u00f3n del servicio: Servicio de mantenimiento de camaras de seguridad\n"
                    "Fecha de emision: 07/05/2025\n"
                    "Monto Total: S/. 1,500.00"
                ),
                confidence=0.9,
                evidence=["orden de servicio"],
            ),
            DocumentSegment(
                document_type="carta_solicitud",
                page_start=1,
                page_end=1,
                text=(
                    "Carta N 045-2025 solicito conformidad.\n"
                    "Adjunto: informe de actividades, recibo por honorarios, fotografias"
                ),
                confidence=0.8,
                evidence=["carta", "adjunto"],
            ),
            DocumentSegment(
                document_type="informe_actividades",
                page_start=3,
                page_end=3,
                text="Actividades realizadas: mantenimiento preventivo durante 25 dias trabajados",
                confidence=0.8,
                evidence=["informe"],
            ),
        ]
    )

    result = FieldExtractor().extract(segmentation)

    assert result.status == "extraido"
    assert by_field(result, "proveedor")[0].value == "SERVICIOS MUNICIPALES DEL SUR SAC"
    assert by_field(result, "proveedor")[0].source == "orden_servicio"
    assert by_field(result, "proveedor")[0].page == 2
    assert by_field(result, "ruc")[0].normalized_value == "20481234567"
    assert by_field(result, "numero_orden_servicio")[0].normalized_value == "0001582"
    assert by_field(result, "monto_total_os")[0].normalized_value == "1500.00"
    assert by_field(result, "concepto")[0].value == "Servicio tecnico"
    assert by_field(result, "descripcion_servicio")[0].value == "Servicio de mantenimiento de camaras de seguridad"
    assert by_field(result, "valor_venta") == []
    assert by_field(result, "igv") == []
    assert by_field(result, "actividades_dias_trabajados") == []
    assert by_field(result, "fecha") == []
    assert by_field(result, "documentos_adjuntos") == []
    assert by_field(result, "numero_carta_informe") == []
    assert all(item.confidence > 0 for item in result.fields)


def test_field_extractor_returns_empty_result_without_matches() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="desconocido",
                page_start=1,
                page_end=1,
                text="Texto sin datos estructurados.",
                confidence=0.0,
                evidence=[],
            )
        ]
    )

    result = FieldExtractor().extract(segmentation)

    assert result.status == "sin_datos_extraidos"
    assert result.fields == []


def test_field_extractor_keeps_page_when_segment_has_multiple_pages() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="orden_servicio",
                page_start=2,
                page_end=3,
                text=(
                    "ORDEN DE SERVICIO N 0001582\n"
                    "RUC: 20481234567"
                    "\n\n"
                    "Monto Total: S/. 1,500.00\n"
                    "IGV 18%: S/. 228.81"
                ),
                confidence=0.9,
                evidence=["orden de servicio"],
            )
        ]
    )

    result = FieldExtractor().extract(segmentation)

    assert by_field(result, "ruc")[0].page == 2
    assert by_field(result, "monto_total_os")[0].page == 3
    assert by_field(result, "igv") == []


def test_field_extractor_trims_ocr_line_fields() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="orden_servicio",
                page_start=11,
                page_end=11,
                text=(
                    "Señor(es) : TITO PAREDES WILLIAM ELAIDY Dirección : AV. NORTE "
                    "RUC : 10426218131 Concepto : SERVICIO TECNICO DE MANTENIMIENTO "
                    "DE COMPUTADORAS 071100431220 SERVICIO [SERVICIOS DIVERSOS "
                    "AFECTACION PRESUPUESTAL Meta/Cadena"
                ),
                confidence=0.9,
                evidence=["orden de servicio"],
            )
        ]
    )

    result = FieldExtractor().extract(segmentation)

    assert by_field(result, "proveedor")[0].value == "TITO PAREDES WILLIAM ELAIDY"
    assert (
        by_field(result, "concepto")[0].value
        == "SERVICIO TECNICO DE MANTENIMIENTO DE COMPUTADORAS"
    )


def test_field_extractor_ignores_recibo_payer_as_provider() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="recibo_honorarios",
                page_start=9,
                page_end=9,
                text=(
                    "TITO PAREDES WILLIAM ELAIDY RU.C, 10426218131 "
                    "Recibi de: MUNICIPALIDAD PROVINCIAL DE PUNO "
                    "Identificado con RUC numero 20146247084 Domicilio del Usuario"
                ),
                confidence=0.8,
                evidence=["recibo"],
            )
        ]
    )

    result = FieldExtractor().extract(segmentation)

    assert by_field(result, "proveedor")[0].value == "TITO PAREDES WILLIAM ELAIDY"
    assert [item.normalized_value for item in by_field(result, "ruc")] == ["10426218131"]


def test_field_extractor_handles_paddle_ocr_order_service_layout() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="orden_servicio",
                page_start=11,
                page_end=11,
                text=(
                    "ORDEN DE SERVICIO N° 0001582 2 "
                    "Señor(es) : TITO PAREDES WILLIAM ELAIDY N° Cuadro Adquisic: 001573 "
                    "Ruc: 10426218131 Concepto : P/S 2100 SERVICIO DE TECNICO EN "
                    "MANTENIMIENTO DE COMPUTADORAS Código Valor Unid. Med. Descripción "
                    "Total S/ 071100431220 SERVICIO SERVICIOS DIVERSOS 3,000.00"
                ),
                confidence=0.9,
                evidence=["orden de servicio"],
            ),
            DocumentSegment(
                document_type="recibo_honorarios",
                page_start=9,
                page_end=9,
                text="Total por honorarios: 1,500.00",
                confidence=0.9,
                evidence=["recibo"],
            ),
        ]
    )

    result = FieldExtractor().extract(segmentation)

    assert by_field(result, "numero_orden_servicio")[0].normalized_value == "0001582"
    assert by_field(result, "proveedor")[0].value == "TITO PAREDES WILLIAM ELAIDY"
    assert (
        by_field(result, "concepto")[0].value
        == "SERVICIO DE TECNICO EN MANTENIMIENTO DE COMPUTADORAS"
    )
    assert [item.normalized_value for item in by_field(result, "monto_entregable")] == ["1500.00"]
    assert by_field(result, "monto_total_os")[0].normalized_value == "3000.00"


def test_field_extractor_handles_paddle_ocr_receipt_header_and_concept() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="recibo_honorarios",
                page_start=3,
                page_end=3,
                text=(
                    "LOPEZ QulspE ZuLEMA ANDREA\n"
                    "JR. TITICACA NRO. 254 PUNO\n"
                    "Recibl de: MUNICIPALIDAD PROVINCIAL DE PUNO\n"
                    "Idontificado con RUC\n"
                    "R.u.C. 10412407127\n"
                    "RECIBO POR lioNORARIOS ELECTRONICO\n"
                    "Por concopto de SERVICIOS PRESTADOS COMO INSPECTOR DE COMERCIO "
                    "AMBULATORIO PARA LA FESTIVIDAD VIRGEN DE LA CANDELARIA "
                    "SEGUN ORDEN DE SERVIclo NRO.00cO452 CORRESPONDIENTE AL UNICO ENTREGABLE\n"
                    "Observacion -\n"
                    "Total por honorarios: 700.00"
                ),
                confidence=0.7,
                evidence=["recibo"],
            )
        ]
    )

    result = FieldExtractor().extract(segmentation)

    assert by_field(result, "proveedor")[0].value == "LOPEZ QulspE ZuLEMA ANDREA"
    assert by_field(result, "ruc")[0].normalized_value == "10412407127"
    assert by_field(result, "numero_orden_servicio")[0].normalized_value == "0000452"
    assert by_field(result, "monto_entregable")[0].normalized_value == "700.00"
    assert "INSPECTOR DE COMERCIO AMBULATORIO" in by_field(result, "concepto")[0].value
    assert "INSPECTOR DE COMERCIO AMBULATORIO" in by_field(result, "descripcion_servicio")[0].value


def test_field_extractor_uses_ocr_order_service_context_for_amount() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="desconocido",
                page_start=2,
                page_end=2,
                text=(
                    "umDAD E.EcuTORA wRO iDEunFicActoN ORDEN "
                    "servlclo sB R_znd pin IA sun GmBNclA "
                    "AFEC CION PRESuPuESTAL S/700.00"
                ),
                confidence=0.0,
                evidence=[],
            )
        ]
    )

    result = FieldExtractor().extract(segmentation)

    assert by_field(result, "monto_total_os")[0].normalized_value == "700.00"


def test_field_extractor_uses_last_importe_total_in_invoice_block() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="factura",
                page_start=3,
                page_end=3,
                text=(
                    "Factura Electronica - Impresion\n"
                    "CORPORACION ROCA WINUYO S.A.C.\n"
                    "RUC: 20612253162\n"
                    "Valor Venta :\n"
                    "Otros Tributos :\n"
                    "Importe Total :\n"
                    "S/ 1,144.07\n"
                    "S/ 0.00\n"
                    "S/ 205.93\n"
                    "S/ 1,350.00\n"
                    "Informacion de la detraccion"
                ),
                confidence=0.9,
                evidence=["factura"],
            )
        ]
    )

    result = FieldExtractor().extract(segmentation)

    assert by_field(result, "proveedor")[0].value == "CORPORACION ROCA WINUYO S.A.C."
    assert by_field(result, "monto_entregable")[0].normalized_value == "1350.00"


def test_field_extractor_extracts_provider_from_acta_context() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="desconocido",
                page_start=4,
                page_end=4,
                text=(
                    "por otra parte el proveedor la empresa CORPORACION ROCA WINUYO "
                    "S.A.C.-con 20612253162, domiciliado en el Jr. San Bartolome"
                ),
                confidence=0.0,
                evidence=[],
            )
        ]
    )

    result = FieldExtractor().extract(segmentation)

    assert by_field(result, "proveedor")[0].value == "CORPORACION ROCA WINUYO S.A.C."


def test_field_extractor_extracts_description_without_colon_from_order_service() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="orden_servicio",
                page_start=2,
                page_end=2,
                text=(
                    "Descripc]6n ALQUILER DE MAQUINARIA COMPACTADORA VIBRATORIO "
                    "TIPO PLANCHA +ORDEN QUE SE EMITE PARA LA CONTRATACION"
                ),
                confidence=0.8,
                evidence=["orden"],
            )
        ]
    )

    result = FieldExtractor().extract(segmentation)

    assert (
        by_field(result, "descripcion_servicio")[0].value
        == "ALQUILER DE MAQUINARIA COMPACTADORA VIBRATORIO TIPO PLANCHA"
    )
    assert by_field(result, "concepto")[0].value == "ALQUILER DE MAQUINARIA COMPACTADORA VIBRATORIO TIPO PLANCHA"


def test_field_extractor_prefers_order_service_table_total_over_budget_noise() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="orden_servicio",
                page_start=5,
                page_end=5,
                text=(
                    "ORDEN DE SERVICIO N 001089 AFECTACION PRESUPUESTAL "
                    "Total S/ REFERENCIA 99,999.50 "
                    "Codigo Unid. Med. Descripcion Total S/ "
                    "071100431220 SERVICIO SERVICIOS DIVERSOS 8,000.00 "
                    "Vienen... 8,000.00"
                ),
                confidence=0.9,
                evidence=["orden de servicio"],
            )
        ]
    )

    result = FieldExtractor().extract(segmentation)

    assert [item.normalized_value for item in by_field(result, "monto_total_os")] == ["8000.00"]
    assert by_field(result, "concepto") == []
    assert by_field(result, "descripcion_servicio") == []


def test_field_extractor_cleans_receipt_header_page_number_from_provider() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="recibo_honorarios",
                page_start=6,
                page_end=6,
                text=(
                    "3 ANDRADE ZAPATA LUIS\n"
                    "R.U.C. 10412345678\n"
                    "RECIBO POR HONORARIOS ELECTRONICO\n"
                    "Total por honorarios: 4,000.00"
                ),
                confidence=0.8,
                evidence=["recibo"],
            )
        ]
    )

    result = FieldExtractor().extract(segmentation)

    assert by_field(result, "proveedor")[0].value == "ANDRADE ZAPATA LUIS"


def test_field_extractor_treats_receipt_amount_as_deliverable_even_with_order_reference() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="recibo_honorarios",
                page_start=9,
                page_end=9,
                text=(
                    "- 02 - 01 TITO PAREDES WILLIAM ELAIDY R.U.C. 10426218131 "
                    "RECIBO POR HONORARIOS ELECTRONICO "
                    "Por concepto de SERVICIO TECNICO SEGUN ORDEN DE SERVICIO 00015 82 "
                    "Total por honorarios: 1,500.00"
                ),
                confidence=0.8,
                evidence=["recibo"],
            )
        ]
    )

    result = FieldExtractor().extract(segmentation)

    assert by_field(result, "proveedor")[0].value == "TITO PAREDES WILLIAM ELAIDY"
    assert by_field(result, "numero_orden_servicio")[0].normalized_value == "0001582"
    assert by_field(result, "monto_entregable")[0].normalized_value == "1500.00"
    assert by_field(result, "monto_total_os") == []


def test_field_extractor_handles_noisy_receipt_header_and_honoraries_ocr() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="recibo_honorarios",
                page_start=4,
                page_end=4,
                text=(
                    "•.|u CUTIPA IVIAIVIANI PEDRO INGENIER0 JR. TUPAC AMARU "
                    "ldentificado con Rue lLU.C. 10416669517 "
                    "RECIBO POF 110NOFtARlos ELECTRONICO "
                    "Par concepto de SERVICIO DE RESPONSABLE TECNICO "
                    "Total pot honoraries: 2, 500.00"
                ),
                confidence=0.8,
                evidence=["recibo"],
            )
        ]
    )

    result = FieldExtractor().extract(segmentation)

    assert by_field(result, "proveedor")[0].value == "CUTIPA MAMANI PEDRO"
    assert by_field(result, "ruc")[0].normalized_value == "10416669517"
    assert by_field(result, "monto_entregable")[0].normalized_value == "2500.00"


def test_field_extractor_skips_budget_amount_context_for_order_fallback() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="orden_servicio",
                page_start=2,
                page_end=2,
                text=(
                    "AFECTACION PRESUPUESTAL Meta/Cadena Funcional Clasif. Gasto "
                    "3999999.5000003 99,999.50 "
                    "TOTAL S/ 5,000.00"
                ),
                confidence=0.8,
                evidence=["orden"],
            )
        ]
    )

    result = FieldExtractor().extract(segmentation)

    assert [field.normalized_value for field in by_field(result, "monto_total_os")] == ["5000.00"]


def test_field_extractor_extracts_service_from_noisy_order_phrase_and_par_concepto() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="orden_servicio",
                page_start=2,
                page_end=2,
                text=(
                    "De8cripcl6n SERVICIOS DIVERSOS +ORDEN QUE SE EMITE PARA LA "
                    "CONTRATACION DE SERVICIO DE RESPONSABLE TECNICO PARA LA SUB "
                    "GERENCIA DE OBRAS PUBLICAS +SEGUN PEDIDO DE SERVICIO"
                ),
                confidence=0.8,
                evidence=["orden"],
            ),
            DocumentSegment(
                document_type="recibo_honorarios",
                page_start=4,
                page_end=4,
                text=(
                    "Par concepto de SERVICIO DE RESPONSABLE TECNICO PARA LA SUB "
                    "GERENCIA DE OBRAS PUBLICAS Observacion -"
                ),
                confidence=0.8,
                evidence=["recibo"],
            ),
        ]
    )

    result = FieldExtractor().extract(segmentation)
    concepts = [field.value for field in by_field(result, "concepto")]

    assert any("RESPONSABLE TECNICO" in value for value in concepts)
    assert any(field.source == "recibo_honorarios" for field in by_field(result, "concepto"))


def test_field_extractor_extracts_service_when_la_is_ocr_as_ia() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="orden_servicio",
                page_start=2,
                page_end=2,
                text=(
                    "+ORDEN QUE SE EMITE PARA IA coNTRATAcl6N DE sERvlclct "
                    "DE REspONSABm TECNlco PARA IA SUB GERENCIA DE OBRAS "
                    "PUBLICAS +SEcON PEDIDO DE SERVICIO"
                ),
                confidence=0.8,
                evidence=["orden"],
            )
        ]
    )

    result = FieldExtractor().extract(segmentation)

    assert "REspONSABm TECNlco" in by_field(result, "concepto")[0].value


def test_field_extractor_extracts_service_when_orden_word_is_noisy() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="orden_servicio",
                page_start=2,
                page_end=2,
                text=(
                    "+ORI>EN QUE sE EMITE PARA IA coNTRATAcl6N DE sERvlclct "
                    "DE REspONSABm TECNlco PARA IA SUB GERENCIA DE OBRAS PUBLICAS, "
                    "CON META pRBsupuESTAL"
                ),
                confidence=0.8,
                evidence=["orden"],
            )
        ]
    )

    result = FieldExtractor().extract(segmentation)

    assert "REspONSABm TECNlco" in by_field(result, "concepto")[0].value


def test_field_extractor_normalizes_os_with_ocr_s_as_five() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="carta_solicitud",
                page_start=1,
                page_end=1,
                text="Ref.: ORDEN DE SERVICIO Nº OOO1S42",
                confidence=0.8,
                evidence=["carta"],
            )
        ]
    )

    result = FieldExtractor().extract(segmentation)

    assert by_field(result, "numero_orden_servicio")[0].normalized_value == "0001542"


def test_field_extractor_normalizes_os_when_year_is_attached() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="carta_solicitud",
                page_start=1,
                page_end=1,
                text="Referencia : ORDEN DE SERVICIO NÂº 00001378 2025-00018035",
                confidence=0.8,
                evidence=["carta"],
            )
        ]
    )

    result = FieldExtractor().extract(segmentation)

    assert by_field(result, "numero_orden_servicio")[0].normalized_value == "0001378"


def test_field_extractor_does_not_treat_securos_version_as_os_number() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="informe_actividades",
                page_start=7,
                page_end=7,
                text="Migrar a versiones recientes de SecurOs 2.3. Soporte tecnico",
                confidence=0.8,
                evidence=["informe"],
            )
        ]
    )

    result = FieldExtractor().extract(segmentation)

    assert by_field(result, "numero_orden_servicio") == []


def test_field_extractor_ignores_invoice_receiver_ruc() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="factura",
                page_start=2,
                page_end=2,
                text=(
                    "FACTURA ELECTRONICA GONZALES VALERO GUIDO RuC: 10012640892 "
                    "MUNICIPALIDAD PROVINCIAL Senor(es) DE PUNO RUC : 20146247084 "
                    "Direccion del Receptor : PLAZA DE ARMAS "
                    "Importe Total : S/ 2,000.00"
                ),
                confidence=0.9,
                evidence=["factura"],
            )
        ]
    )

    result = FieldExtractor().extract(segmentation)

    assert [item.normalized_value for item in by_field(result, "ruc")] == ["10012640892"]


def test_field_extractor_rejects_compact_total_as_service_text() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="orden_servicio",
                page_start=5,
                page_end=5,
                text="Descripcion TotalS/ 500 00050561 SERVICIO DE IMPRESIONES EN GENERAL",
                confidence=0.8,
                evidence=["orden"],
            )
        ]
    )

    result = FieldExtractor().extract(segmentation)

    assert by_field(result, "concepto") == []
    assert by_field(result, "descripcion_servicio") == []


def test_field_extractor_rejects_address_as_provider_and_uses_de_provider() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="carta_solicitud",
                page_start=1,
                page_end=1,
                text=(
                    "DE : Yemar Jhusbel CHAHUARE$ FLORES. PROVEEDOR. "
                    "Jr. Eladio Quiroga N° 160 - Puno."
                ),
                confidence=0.8,
                evidence=["carta"],
            ),
            DocumentSegment(
                document_type="factura",
                page_start=7,
                page_end=7,
                text=(
                    "CHAHUARES FLORES YEMAR JHUSBEL FACTURA ELECTRONICA\n"
                    "JR. ELADIO QUIROGA 160\n"
                    "Ruc: 10455140094"
                ),
                confidence=0.9,
                evidence=["factura"],
            ),
        ]
    )

    result = FieldExtractor().extract(segmentation)
    providers = [field.value for field in by_field(result, "proveedor")]

    assert "Jr. Eladio Quiroga N° 160 - Puno." not in providers
    assert "Yemar Jhusbel CHAHUARES FLORES." in providers
    assert "CHAHUARES FLORES YEMAR JHUSBEL" in providers


def test_field_extractor_trims_order_service_provider_before_process_type() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="orden_servicio",
                page_start=3,
                page_end=3,
                text=(
                    "Señor(es) : CHAHUARES FLORES YEMAR JHUSBEL "
                    "Tipo de Proceso : ASp - N* 0055-2025-MPP "
                    "Dirección : JR. ELADIO QUIROGA 160"
                ),
                confidence=0.9,
                evidence=["orden"],
            )
        ]
    )

    result = FieldExtractor().extract(segmentation)

    assert [field.value for field in by_field(result, "proveedor")] == [
        "CHAHUARES FLORES YEMAR JHUSBEL"
    ]


def test_field_extractor_removes_single_order_service_outlier_when_main_os_repeats() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="carta_solicitud",
                page_start=1,
                page_end=1,
                text="Referencia : ORDEN DE SERVICIO Nº 00001378 2025-00018035",
                confidence=0.8,
                evidence=["carta"],
            ),
            DocumentSegment(
                document_type="factura",
                page_start=2,
                page_end=2,
                text="Descripcion: SERVICIO SEGUN ORDEN DE SERVICIO 0001378",
                confidence=0.9,
                evidence=["factura"],
            ),
            DocumentSegment(
                document_type="orden_servicio",
                page_start=4,
                page_end=4,
                text="ORDEN DE SERVICIO N° 0001378 MUNICIPALIDAD PROVINCIAL DE PUNO",
                confidence=0.9,
                evidence=["orden"],
            ),
            DocumentSegment(
                document_type="orden_servicio",
                page_start=5,
                page_end=5,
                text="ORDEN DE SERVICIO N° 0000031 DIRECCION REGIONAL AGRARIA DE PUNO",
                confidence=0.9,
                evidence=["orden"],
            ),
        ]
    )

    result = FieldExtractor().extract(segmentation)

    assert [field.normalized_value for field in by_field(result, "numero_orden_servicio")] == [
        "0001378",
        "0001378",
        "0001378",
    ]
    assert all(field.page != 5 for field in result.fields)


def test_field_extractor_ignores_cui_decimal_as_order_amount() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="orden_servicio",
                page_start=3,
                page_end=3,
                text=(
                    "Concepto : SERVICIO DE ALQUILER DE CAMIONETA "
                    "Valor Codigo Descripcion Total S/ Unid. Med. 7,500.00 "
                    "942000030010 SERVICIO ALQUILER DE CAMIONETA Meta "
                    "21.046.0102.0101.2393867.4000166 CON CUI "
                    "2393867.4000166"
                ),
                confidence=0.9,
                evidence=["orden"],
            )
        ]
    )

    result = FieldExtractor().extract(segmentation)

    assert [field.normalized_value for field in by_field(result, "monto_total_os")] == ["7500.00"]


def test_field_extractor_trims_ocr_footer_from_provider() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="carta_solicitud",
                page_start=1,
                page_end=1,
                text=(
                    "DE : Yemar Jhusbel CHAHUARES FLORES. Pch 27/03/2025 "
                    "13:41:22 Aee.: usuario Trb.Amb.:1153d PROVEEDOR."
                ),
                confidence=0.8,
                evidence=["carta"],
            )
        ]
    )

    result = FieldExtractor().extract(segmentation)

    assert by_field(result, "proveedor")[0].value == "Yemar Jhusbel CHAHUARES FLORES."


def test_field_extractor_extracts_responsable_from_formal_de_line() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="carta_solicitud",
                page_start=1,
                page_end=1,
                text=(
                    "DE\n"
                    ": ING. PEDRO CUTIPA MAMANI\n"
                    "RESPONSABLE TECNICO DE MANTENIMIENTO DE VIAS"
                ),
                confidence=0.8,
                evidence=["carta"],
            ),
            DocumentSegment(
                document_type="informe_actividades",
                page_start=6,
                page_end=6,
                text=(
                    "DE : ING. PEDRO CUTIPA MAMANI "
                    "RESPONSABLE TECNICO - MANTENIMIENTO DE VIAS"
                ),
                confidence=0.8,
                evidence=["informe"],
            ),
        ]
    )

    result = FieldExtractor().extract(segmentation)
    providers = [field.value for field in by_field(result, "proveedor")]

    assert "PEDRO CUTIPA MAMANI" in providers
    assert all(provider == "PEDRO CUTIPA MAMANI" for provider in providers)


def test_field_extractor_ignores_attachment_list_as_provider() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="recibo_honorarios",
                page_start=2,
                page_end=2,
                text=(
                    "Segundo. - Anexo a la presente copia de los siguientes: "
                    "COPIA DE DNI ORDEN DE SERVICIO No 001089 "
                    "RECIBO POR HONORARIOS ELECTRONICO"
                ),
                confidence=0.7,
                evidence=["recibo por honorarios"],
            )
        ]
    )

    result = FieldExtractor().extract(segmentation)

    assert by_field(result, "proveedor") == []
    assert by_field(result, "numero_orden_servicio")[0].normalized_value == "0001089"


def test_field_extractor_removes_single_digit_ruc_ocr_outlier() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="carta_solicitud",
                page_start=1,
                page_end=1,
                text="RUC: 10455140094",
                confidence=0.8,
                evidence=["carta"],
            ),
            DocumentSegment(
                document_type="orden_servicio",
                page_start=3,
                page_end=3,
                text="RUC: 10455140094",
                confidence=0.9,
                evidence=["orden"],
            ),
            DocumentSegment(
                document_type="orden_servicio",
                page_start=5,
                page_end=5,
                text="Pie OCR RUC: 10455140084",
                confidence=0.4,
                evidence=["orden"],
            ),
            DocumentSegment(
                document_type="factura",
                page_start=7,
                page_end=7,
                text="RUC: 10455140094 FACTURA ELECTRONICA",
                confidence=0.9,
                evidence=["factura"],
            ),
        ]
    )

    result = FieldExtractor().extract(segmentation)

    assert [field.normalized_value for field in by_field(result, "ruc")] == [
        "10455140094",
        "10455140094",
        "10455140094",
    ]


def test_field_extractor_extracts_deliverable_schedule_from_noisy_order_service() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="orden_servicio",
                page_start=2,
                page_end=2,
                text=(
                    "+roRMA DE pAGo: EL pAco sE REALlzARA EN o2 ENTREGABLEs. "
                    "+PRIMER ENTREGABLE: (5Os DEL TOTAL) INFORME DE ACTIVIDADES. "
                    "+SEGUND0 ENTREGABLE: (SOS DEL TOTAL) INFORME DE ACTIVIDADES."
                ),
                confidence=0.8,
                evidence=["orden"],
            )
        ]
    )

    result = FieldExtractor().extract(segmentation)

    assert [field.normalized_value for field in by_field(result, "numero_entregables")] == ["2"]
    assert [field.normalized_value for field in by_field(result, "porcentaje_entregable")] == [
        "1:50",
        "2:50",
    ]


def test_field_extractor_extracts_unique_deliverable_schedule() -> None:
    segmentation = build_segmentation(
        [
            DocumentSegment(
                document_type="recibo_honorarios",
                page_start=4,
                page_end=4,
                text="SEGUN ORDEN DE SERVIclo NRO.00cO452 CORRESPONDIENTE AL UNICO ENTREGABLE",
                confidence=0.8,
                evidence=["recibo"],
            )
        ]
    )

    result = FieldExtractor().extract(segmentation)

    assert [field.normalized_value for field in by_field(result, "numero_entregables")] == ["1"]
