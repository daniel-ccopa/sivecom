import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from app.models.document_segment import DocumentSegmentationResult, DocumentSegment
from app.models.extracted_data import DataExtractionResult, ExtractedDatum
from app.services.data_extraction.normalization import (
    clean_line_value,
    normalize_amount,
    normalize_ruc,
    normalize_spaces,
    normalize_text,
)


NUMBER_MARKER = r"(?:N(?:\.|Â?[\u00b0\u00ba])?|No\.?|Nro\.?)"
SERVICE_WORD = r"SERV(?:ICIO|[I1l]C[I1l]O)"
OS_NUMBER_VALUE = r"[0-9Oo](?:[\s.\-]*[0-9Oo]|(?<=[0-9Oo])[\s.\-]*[CcSs](?=[0-9Oo])){3,13}"

RUC_PATTERN = re.compile(
    rf"(?:R\.?\s*U\.?[\.,]?\s*C\.?[\.,]?|[I1l]L?U\.?[\.,]?\s*C\.?[\.,]?|RUC)\s*(?:{NUMBER_MARKER}|:|-)?\s*(\d{{11}})",
    re.IGNORECASE,
)
OS_PATTERN = re.compile(
    rf"(?:ORDEN\s+DE\s+{SERVICE_WORD}|O/S|O\.S\.|OS\s+{NUMBER_MARKER})\s*{NUMBER_MARKER}?\s*[:.\-]?\s*({OS_NUMBER_VALUE})",
    re.IGNORECASE,
)
TOTAL_PATTERN = re.compile(
    r"(?:TOTAL\s+P[O0][RT]\s+HONORAR(?:IOS|IES|[I1l]OS)|TOTAL\s+NETO\s+RECIBIDO|TOTAL\s+NATO\s+ROC[I1l]B[I1l]DO|MONTO\s+TOTAL|IMPORTE\s+TOTAL|TOTAL)\s*[:\-]?\s*(?:S/\.?)?\s*([0-9][0-9.,\s]*)",
    re.IGNORECASE,
)
OS_AMOUNT_PATTERN = re.compile(
    r"(?:S/\.?\s*)?([0-9]{1,3}(?:,[0-9]{3})+\.[0-9]{2}|[0-9]+\.[0-9]{2})",
    re.IGNORECASE,
)
ORDER_TABLE_AMOUNT_PATTERN = re.compile(
    rf"\b{SERVICE_WORD}\s+SERV(?:ICIOS|[I1l]C[I1l]OS)\s+DIVERSOS\s+"
    r"([0-9]{1,3}(?:,[0-9]{3})+\.[0-9]{2}|[0-9]+\.[0-9]{2})",
    re.IGNORECASE,
)
ORDER_VIENEN_AMOUNT_PATTERN = re.compile(
    r"\b(?:Vienen|Van)\.?\s*"
    r"([0-9]{1,3}(?:,[0-9]{3})+\.[0-9]{2}|[0-9]+\.[0-9]{2})",
    re.IGNORECASE,
)
INVOICE_TOTAL_BLOCK_PATTERN = re.compile(
    r"Importe\s+Total\s*:?\s*(?P<block>.+?)(?:Informaci[o6]n\s+de\s+la\s+detracci[o6]n|Leyenda|Esta\s+es\s+una|$)",
    re.IGNORECASE | re.DOTALL,
)
DELIVERABLE_COUNT_PATTERN = re.compile(
    r"\b(?:EN\s+)?([0-9Oo]{1,2})\s+ENTREGABLES?\b",
    re.IGNORECASE,
)
UNIQUE_DELIVERABLE_PATTERN = re.compile(
    r"\b(?:UNICO|UNICA|[Uu]NICO)\s+ENTREGABLE\b",
    re.IGNORECASE,
)
DELIVERABLE_PERCENT_PATTERN = re.compile(
    r"\b([A-Z0-9]{4,10}|\d{1,2})\s+ENTREGABLE\b"
    r".{0,80}?\(?\s*([0-9OoSs%]{2,4})\s*(?:DEL\s+TOTAL|TOTAL|%)",
    re.IGNORECASE | re.DOTALL,
)
RECEIPT_OR_INVOICE_PROVIDER_LIMIT_PATTERN = re.compile(
    r"\b(?:RECIB[I1l]\s+DE|RECIBO\s+POR|RECIBO\s+PO[FRT]|R\.?\s*U\.?[\.,]?\s*C\.?|[I1l]L?U\.?[\.,]?\s*C\.?)\b",
    re.IGNORECASE,
)
LINE_PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    "proveedor": (
        re.compile(
            r"(?:Proveedor(?!\s+de\s+servicios)|Nombre/Raz[\u00f3o]n Social|Raz[\u00f3o]n Social|Se[\u00f1n]or\(es\)|Sefior\(es\))\s*[:\-]\s*(.+)",
            re.IGNORECASE,
        ),
        re.compile(
            r"[:\-]\s*([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s.&'-]{6,120}?)\.?\s+Proveedor\s+de\s+servicios\b",
            re.IGNORECASE,
        ),
        re.compile(
            r"(?:por\s+otra\s+parte\s+el\s+proveedor\s+la\s+empresa|proveedor\s+la\s+empresa)\s+(.+?)(?:[-,]?\s*con\s+(?:R\.?\s*U\.?\s*C\.?)?\s*\d{11}|\s+domiciliad[oa]|\n|$)",
            re.IGNORECASE | re.DOTALL,
        ),
        re.compile(
            r"\bDE\s*[:.\-•]+\s*(.+?)\s+PROVEEDOR\b",
            re.IGNORECASE | re.DOTALL,
        ),
        re.compile(
            r"\bDE\b.{0,120}?[:.\-:]+\s*(?:ING\.?\s*)?([A-ZÃÃ‰ÃÃ“ÃšÃ‘][A-ZÃÃ‰ÃÃ“ÃšÃ‘\s.&'-]{6,120}?)\s+RESPONSABLE\b",
            re.IGNORECASE | re.DOTALL,
        ),
        re.compile(
            r"\bDE\b.{0,80}?[:.\-:]+\s*(?:ING\.?\s*)?([A-ZÃÃ‰ÃÃ“ÃšÃ‘][A-ZÃÃ‰ÃÃ“ÃšÃ‘\s.&'-]{6,120}?)(?:\n|$)",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    "concepto": (
        re.compile(
            r"(?:Concepto)\s*(?:del servicio)?\s*[:\-]\s*(.+)",
            re.IGNORECASE,
        ),
        re.compile(
            r"D[e8]scripc\S*n(?!\s+DE\s+)\s+(.+?)(?:\+ORDEN\s+QUE\s+SE|\bAFECTACION\b|\bMeta/|\bVan\.\.\.|\bTotal\b|$)",
            re.IGNORECASE | re.DOTALL,
        ),
        re.compile(
            r"ORDEN\s+QUE\s+SE\s+EMITE\s+PARA\s+[LI][AA]\s+CONTRATA\w*\s+DE\s+(.+?)(?:\+SEG[Uu]\w*N|\*SEG[Uu]\w*N|\+LUGAR|\*LUGAR|\bAFECTACION\b|$)",
            re.IGNORECASE | re.DOTALL,
        ),
        re.compile(
            r"QUE\s+S?E\s+EMITE\s+PARA\s+[LI][AA]\s+CONTRATA\w*\s+DE\s+(.+?)(?:\+SEG[Uu]\w*N|\*SEG[Uu]\w*N|\+LUGAR|\*LUGAR|\bCON\s+META\b|\bAFECTACION\b|$)",
            re.IGNORECASE | re.DOTALL,
        ),
        re.compile(
            r"(?:ASUNTO)\s*[:\-]\s*(.+?)(?:\bREF\.?\b|\bREFERENCIA\b|\bFECHA\b|\bTengo\b|$)",
            re.IGNORECASE | re.DOTALL,
        ),
        re.compile(
            rf"(?:P[oa]r\s+conc[eo]pto\s+de)\s+(.+?)(?:\bObservac\w*n\b|\bInciso\b|\blncl\w*o\b|\bFecha\b|\bFochadeem\w*n\b|\bTotal\b|$)",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    "descripcion_servicio": (
        re.compile(
            r"(?:Descripci[\u00f3o]n|Detalle)\s*(?:del servicio)?\s*[:\-]\s*(.+)",
            re.IGNORECASE,
        ),
        re.compile(
            r"D[e8]scripc\S*n(?!\s+DE\s+)\s+(.+?)(?:\+ORDEN\s+QUE\s+SE|\bAFECTACION\b|\bMeta/|\bVan\.\.\.|\bTotal\b|$)",
            re.IGNORECASE | re.DOTALL,
        ),
        re.compile(
            r"ORDEN\s+QUE\s+SE\s+EMITE\s+PARA\s+[LI][AA]\s+CONTRATA\w*\s+DE\s+(.+?)(?:\+SEG[Uu]\w*N|\*SEG[Uu]\w*N|\+LUGAR|\*LUGAR|\bAFECTACION\b|$)",
            re.IGNORECASE | re.DOTALL,
        ),
        re.compile(
            r"QUE\s+S?E\s+EMITE\s+PARA\s+[LI][AA]\s+CONTRATA\w*\s+DE\s+(.+?)(?:\+SEG[Uu]\w*N|\*SEG[Uu]\w*N|\+LUGAR|\*LUGAR|\bCON\s+META\b|\bAFECTACION\b|$)",
            re.IGNORECASE | re.DOTALL,
        ),
        re.compile(
            rf"(?:P[oa]r\s+conc[eo]pto\s+de)\s+(.+?)(?:\bObservac\w*n\b|\bInciso\b|\blncl\w*o\b|\bFecha\b|\bFochadeem\w*n\b|\bTotal\b|$)",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
}

LINE_FIELD_STOP_PATTERNS: dict[str, tuple[str, ...]] = {
    "proveedor": (
        r"\bDirecci[o\u00f3]n\b",
        r"\bDireccl6n\b",
        r"\bR\.?\s*U\.?\s*C\.?\b",
        r"\bTel[e\u00e9]fono\b",
        r"\bConcepto\b",
        r"\bTipo\s+de\s+Proceso\b",
        r"\bCCI\b",
        r"\bN\s*[\u00b0\u00ba]?\s*Contrato\b",
        r"\bN\s*[\u00b0\u00ba]?\s*Cuadro\s+Adquisic\b",
        r"\bDomicilio\b",
        r"\bdomiciliad[oa]\b",
        r"\bForma\s+de\s+Pago\b",
        r"\bLa\s+suma\s+de\b",
        r"\bPor\s+concepto\s+de\b",
        r"\bFecha\s+de\s+emisi[o\u00f3]n\b",
        r"\+ORDEN\s+QUE\s+SE\b",
        r"\bSub\s*$",
        r"\bSub\s+Total\b",
    ),
    "concepto": (
        r"\b\d{8,}\s+SERVICIO\b",
        r"\bC[o\u00f3]digo\s+Valor\b",
        r"\bC[o\u00f3]digo\s+Unid\b",
        r"\bC[o\u00f3]digo\b",
        r"\bUnid\.?\s+Med\.?\b",
        r"\bDescripci[o\u00f3]n\s+Total\s+S/?\b",
        r"\bLUGAR\s+Y\s+PLAZO\b",
        r"\bFORMA\s+DE\s+PAGO\b",
        r"\bTotal\s+S/?\b",
        r"\bAFECTACI[O\u00d3]N\s+PRESUPUESTAL\b",
        r"\bMeta/\s*Cadena\b",
        r"\bNOTA\s+IMPORTANTE\b",
        r"\bExonerado\b",
        r"\bV\.?\s*Venta\b",
        r"\bI\.?\s*G\.?\s*V\.?\b",
        r"\bObservaci[o\u00f3]n\b",
        r"\bFecha\s+de\s+emisi[o\u00f3]n\b",
    ),
    "descripcion_servicio": (
        r"\b\d{8,}\s+SERVICIO\b",
        r"\bC[o\u00f3]digo\s+Valor\b",
        r"\bC[o\u00f3]digo\s+Unid\b",
        r"\bC[o\u00f3]digo\b",
        r"\bUnid\.?\s+Med\.?\b",
        r"\bDescripci[o\u00f3]n\s+Total\s+S/?\b",
        r"\bLUGAR\s+Y\s+PLAZO\b",
        r"\bFORMA\s+DE\s+PAGO\b",
        r"\bTotal\s+S/?\b",
        r"\bAFECTACI[O\u00d3]N\s+PRESUPUESTAL\b",
        r"\bMeta/\s*Cadena\b",
        r"\bNOTA\s+IMPORTANTE\b",
        r"\bExonerado\b",
        r"\bV\.?\s*Venta\b",
        r"\bI\.?\s*G\.?\s*V\.?\b",
        r"\bObservaci[o\u00f3]n\b",
        r"\bFecha\s+de\s+emisi[o\u00f3]n\b",
        r"\+ORDEN\s+QUE\s+SE\b",
        r"\bSub\s*$",
        r"\bSub\s+Total\b",
    ),
}

LINE_FIELD_MAX_LENGTH: dict[str, int] = {
    "proveedor": 120,
    "concepto": 220,
    "descripcion_servicio": 300,
}


class FieldExtractor:
    def extract(self, segmentation: DocumentSegmentationResult) -> DataExtractionResult:
        fields: list[ExtractedDatum] = []
        for segment in segmentation.segments:
            fields.extend(self.extract_from_segment(segment))

        fields = deduplicate_fields(fields)
        fields = remove_single_source_os_outliers(fields)
        fields = remove_single_ruc_ocr_outliers(fields)
        fields = ensure_description_from_concept(fields)
        fields = ensure_concept_from_description(fields)
        status = "extraido" if fields else "sin_datos_extraidos"
        return DataExtractionResult(
            expediente_id=segmentation.expediente_id,
            status=status,
            fields=fields,
            extracted_at=datetime.now(timezone.utc),
        )

    def extract_from_segment(self, segment: DocumentSegment) -> list[ExtractedDatum]:
        extracted: list[ExtractedDatum] = []
        for page_segment in split_segment_pages(segment):
            extracted.extend(self._extract_ruc(page_segment))
            extracted.extend(self._extract_os_number(page_segment))
            extracted.extend(self._extract_deliverable_schedule(page_segment))
            extracted.extend(self._extract_amounts(page_segment))
            extracted.extend(self._extract_header_provider(page_segment))
            extracted.extend(self._extract_line_fields(page_segment))
        return extracted

    def _make_datum(
        self,
        field: str,
        value: str,
        normalized_value: str,
        segment: DocumentSegment,
        confidence: float,
        evidence: str,
    ) -> ExtractedDatum:
        return ExtractedDatum(
            field=field,
            value=clean_line_value(value),
            normalized_value=normalized_value,
            source=segment.document_type,
            page=segment.page_start,
            confidence=confidence,
            evidence=normalize_spaces(evidence),
        )

    def _extract_ruc(self, segment: DocumentSegment) -> list[ExtractedDatum]:
        fields: list[ExtractedDatum] = []
        for match in RUC_PATTERN.finditer(segment.text):
            normalized_ruc = normalize_ruc(match.group(1))
            if is_payer_ruc_context(
                segment.text,
                match.start(),
                match.end(),
                normalized_ruc,
            ):
                continue
            fields.append(
                self._make_datum(
                    field="ruc",
                    value=match.group(1),
                    normalized_value=normalized_ruc,
                    segment=segment,
                    confidence=0.95,
                    evidence=match.group(0),
                )
            )
        return fields

    def _extract_os_number(self, segment: DocumentSegment) -> list[ExtractedDatum]:
        confidence = 0.95 if segment.document_type == "orden_servicio" else 0.85
        fields: list[ExtractedDatum] = []
        for match in OS_PATTERN.finditer(segment.text):
            normalized_os = normalize_os_number(match.group(1))
            fields.append(
                self._make_datum(
                    field="numero_orden_servicio",
                    value=normalized_os,
                    normalized_value=normalized_os,
                    segment=segment,
                    confidence=confidence,
                    evidence=match.group(0),
                )
            )
        return fields

    def _extract_deliverable_schedule(self, segment: DocumentSegment) -> list[ExtractedDatum]:
        if (
            segment.document_type not in {"orden_servicio", "recibo_honorarios", "factura"}
            and not has_order_service_context(segment)
        ):
            return []

        fields: list[ExtractedDatum] = []
        count_match = DELIVERABLE_COUNT_PATTERN.search(segment.text)
        if count_match:
            count = parse_deliverable_count(count_match.group(1))
            if count is not None and 1 <= count <= 6:
                fields.append(
                    self._make_datum(
                        field="numero_entregables",
                        value=f"{count} entregable{'s' if count != 1 else ''}",
                        normalized_value=str(count),
                        segment=segment,
                        confidence=0.86,
                        evidence=count_match.group(0),
                    )
                )
        elif unique_match := UNIQUE_DELIVERABLE_PATTERN.search(segment.text):
            fields.append(
                self._make_datum(
                    field="numero_entregables",
                    value="1 entregable",
                    normalized_value="1",
                    segment=segment,
                    confidence=0.82,
                    evidence=unique_match.group(0),
                )
            )

        for match in DELIVERABLE_PERCENT_PATTERN.finditer(segment.text):
            ordinal = parse_deliverable_ordinal(match.group(1))
            percent = parse_deliverable_percent(match.group(2))
            if ordinal is None or percent is None or not 0 < percent <= 100:
                continue
            fields.append(
                self._make_datum(
                    field="porcentaje_entregable",
                    value=f"Entregable {ordinal}: {percent}%",
                    normalized_value=f"{ordinal}:{percent}",
                    segment=segment,
                    confidence=0.84,
                    evidence=match.group(0),
                )
            )
        return fields

    def _extract_amounts(self, segment: DocumentSegment) -> list[ExtractedDatum]:
        fields: list[ExtractedDatum] = []
        amount_field = amount_field_for_segment(segment)
        if amount_field == "monto_total_os":
            order_total = extract_order_service_total(segment.text)
            if order_total:
                return [
                    self._make_datum(
                        field="monto_total_os",
                        value=order_total,
                        normalized_value=normalize_amount(order_total),
                        segment=segment,
                        confidence=0.88,
                        evidence=f"Total de tabla O/S: {order_total}",
                    )
                ]
        if amount_field == "monto_entregable" and is_invoice_context(segment):
            invoice_total = extract_invoice_total(segment.text)
            if invoice_total:
                return [
                    self._make_datum(
                        field="monto_entregable",
                        value=invoice_total,
                        normalized_value=normalize_amount(invoice_total),
                        segment=segment,
                        confidence=0.92,
                        evidence=f"Importe Total: {invoice_total}",
                    )
                ]
        for match in TOTAL_PATTERN.finditer(segment.text):
            if is_embedded_numeric_match(segment.text, match.start(1), match.end(1)):
                continue
            normalized_amount = normalize_amount(match.group(1))
            parsed_amount = parse_amount(normalized_amount)
            if is_probable_catalog_code_amount(
                match.group(1), normalized_amount
            ) or is_budget_amount_context(segment.text, match.start(), match.end()):
                continue
            if amount_field == "monto_total_os" and (
                parsed_amount is None or parsed_amount < Decimal("100")
            ):
                continue
            fields.append(
                self._make_datum(
                    field=amount_field,
                    value=match.group(1),
                    normalized_value=normalized_amount,
                    segment=segment,
                    confidence=0.9,
                    evidence=match.group(0),
                )
            )
        if amount_field == "monto_total_os" and not fields_by_field(fields, "monto_total_os"):
            candidates: list[tuple[Decimal, str, str]] = []
            for match in OS_AMOUNT_PATTERN.finditer(segment.text):
                if is_embedded_numeric_match(segment.text, match.start(1), match.end(1)):
                    continue
                normalized_amount = normalize_amount(match.group(1))
                if is_probable_catalog_code_amount(
                    match.group(1), normalized_amount
                ) or is_budget_amount_context(segment.text, match.start(), match.end()):
                    continue
                parsed = parse_amount(normalized_amount)
                if parsed is None or parsed < Decimal("100"):
                    continue
                candidates.append((parsed, match.group(1), match.group(0)))
            if candidates:
                _, raw_value, evidence = max(candidates, key=lambda item: item[0])
                fields.append(
                    self._make_datum(
                        field="monto_total_os",
                        value=raw_value,
                        normalized_value=normalize_amount(raw_value),
                        segment=segment,
                        confidence=0.72,
                        evidence=evidence,
                    )
                )
        return fields

    def _extract_header_provider(self, segment: DocumentSegment) -> list[ExtractedDatum]:
        if (
            segment.document_type not in {"factura", "recibo_honorarios"}
            and not has_receipt_or_invoice_context(segment)
        ):
            return []

        provider = provider_from_document_header(segment.text)
        if not provider:
            return []

        return [
            self._make_datum(
                field="proveedor",
                value=provider,
                normalized_value=normalize_text(provider),
                segment=segment,
                confidence=0.78 if segment.document_type == "desconocido" else 0.86,
                evidence=provider,
            )
        ]

    def _extract_line_fields(self, segment: DocumentSegment) -> list[ExtractedDatum]:
        fields: list[ExtractedDatum] = []
        for field, patterns in LINE_PATTERNS.items():
            for pattern in patterns:
                for match in pattern.finditer(segment.text):
                    value = clean_line_field(field, match.group(1))
                    if not value:
                        continue
                    fields.append(
                        self._make_datum(
                            field=field,
                            value=value,
                            normalized_value=normalize_text(value),
                            segment=segment,
                            confidence=confidence_for_field(field, segment.document_type),
                            evidence=value,
                        )
                    )
        return fields

def confidence_for_field(field: str, document_type: str) -> float:
    if field == "proveedor" and document_type in {"orden_servicio", "factura", "recibo_honorarios"}:
        return 0.88
    if field in {"concepto", "descripcion_servicio"} and document_type == "orden_servicio":
        return 0.82
    return 0.75


def amount_field_for_segment(segment: DocumentSegment) -> str:
    if segment.document_type in {"factura", "recibo_honorarios"} or has_receipt_or_invoice_context(segment):
        return "monto_entregable"
    if segment.document_type == "orden_servicio" or has_order_service_context(segment):
        return "monto_total_os"
    return "monto_entregable"


def fields_by_field(fields: list[ExtractedDatum], field_name: str) -> list[ExtractedDatum]:
    return [field for field in fields if field.field == field_name]


def parse_amount(value: str) -> Decimal | None:
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return None


def normalize_os_number(value: str) -> str:
    corrected_tokens: list[str] = []
    for token in re.findall(r"[0-9OoCcSs]+", value):
        selected_length = len(re.sub(r"\D", "", "".join(corrected_tokens)))
        if selected_length >= 7:
            break
        corrected_token = (
            token.replace("O", "0")
            .replace("o", "0")
            .replace("C", "0")
            .replace("c", "0")
            .replace("S", "5")
            .replace("s", "5")
        )
        if selected_length >= 4 and re.fullmatch(r"20\d{2}", corrected_token):
            break
        if selected_length >= 6 and len(corrected_token) <= 2:
            break
        corrected_tokens.append(corrected_token)

    digits = re.sub(r"\D", "", "".join(corrected_tokens))
    if not digits:
        return value
    while len(digits) > 7 and digits.startswith("0"):
        digits = digits[1:]
    return digits


def parse_deliverable_count(value: str) -> int | None:
    digits = re.sub(r"\D", "", value.replace("O", "0").replace("o", "0"))
    if not digits:
        return None
    return int(digits)


def parse_deliverable_ordinal(value: str) -> int | None:
    normalized = normalize_text(value).replace("0", "o").replace("1", "i")
    ordinals = {
        "primer": 1,
        "primero": 1,
        "segundo": 2,
        "tercer": 3,
        "tercero": 3,
        "cuarto": 4,
        "quinto": 5,
    }
    if normalized in ordinals:
        return ordinals[normalized]
    digits = re.sub(r"\D", "", normalized)
    return int(digits) if digits else None


def parse_deliverable_percent(value: str) -> int | None:
    compact = re.sub(r"[^0-9OoSs]", "", value).upper()
    if not compact:
        return None
    if re.fullmatch(r"[5S][0O][S]?", compact):
        return 50

    corrected = compact.replace("O", "0")
    digits = re.sub(r"\D", "", corrected)
    if not digits:
        return None
    percent = int(digits[:3])
    if percent > 100 and digits.startswith("50"):
        return 50
    return percent


def is_probable_catalog_code_amount(raw_value: str, normalized_value: str) -> bool:
    whole_number = normalized_value.split(".", 1)[0]
    return len(re.sub(r"\D", "", raw_value)) >= 9 and len(whole_number) >= 9


def is_embedded_numeric_match(text: str, start: int, end: int) -> bool:
    before = text[start - 1] if start > 0 else " "
    after = text[end] if end < len(text) else " "
    return before.isdigit() or before == "." or after.isdigit() or after == "."


def is_budget_amount_context(text: str, start: int, end: int) -> bool:
    context = normalize_text(text[max(0, start - 90) : min(len(text), end + 90)])
    immediate_context = normalize_text(text[max(0, start - 20) : end])
    if "total s" in immediate_context:
        return False
    budget_markers = (
        "cadena funcional",
        "clasif gasto",
        "clasif. gasto",
        "monto mnemonica",
        "monto mnem",
        "meta cadena",
        "3999999",
        "5000003",
        "cui",
    )
    if any(marker in context for marker in budget_markers):
        return True
    return "afectacion presupuestal" in context and "total s" not in context


def is_payer_ruc_context(text: str, start: int, end: int, normalized_ruc: str) -> bool:
    if normalized_ruc.startswith("10"):
        return False

    before = normalize_text(text[max(0, start - 80) : start])
    after = normalize_text(text[end : min(len(text), end + 80)])
    context = f"{before} {after}"
    if any(
        marker in context
        for marker in (
            "identificado con ruc",
            "domicilio del usuario",
            "direccion del receptor",
            "direccion del cliente",
        )
    ):
        return True

    before_markers = (
        "senor(es)",
        "senor es",
        "municipalidad provincial",
    )
    return any(marker in before for marker in before_markers)


def has_order_service_context(segment: DocumentSegment) -> bool:
    text = normalize_text(segment.text)
    return any(
        marker in text
        for marker in (
            "orden de servicio",
            "orden de servlclo",
            "unidad ejecutora",
            "umdad e.ecutora",
            "nro identificacion",
            "wro ideunficacion",
            "afectacion presupuestal",
        )
    )


def has_receipt_or_invoice_context(segment: DocumentSegment) -> bool:
    text = normalize_text(segment.text)
    return any(
        marker in text
        for marker in (
            "recibo por lionorarios",
            "recibo por honorarios",
            "recibo pof",
            "recibo por 110no",
            "honorarios electronico",
            "honoraries",
            "total por honorarios",
            "total pot honoraries",
            "recibi de",
            "factura electronica",
            "factuiia electronica",
            "importe total",
        )
    )


def is_invoice_context(segment: DocumentSegment) -> bool:
    text = normalize_text(segment.text)
    return segment.document_type == "factura" or "factura electronica" in text or "factuiia electronica" in text


def extract_invoice_total(text: str) -> str | None:
    match = INVOICE_TOTAL_BLOCK_PATTERN.search(text)
    if not match:
        return None
    candidates = [item.group(1) for item in OS_AMOUNT_PATTERN.finditer(match.group("block"))]
    if not candidates:
        return None
    return candidates[-1]


def extract_order_service_total(text: str) -> str | None:
    candidates: list[tuple[Decimal, str]] = []
    for pattern in (ORDER_TABLE_AMOUNT_PATTERN, ORDER_VIENEN_AMOUNT_PATTERN):
        for match in pattern.finditer(text):
            normalized_amount = normalize_amount(match.group(1))
            parsed = parse_amount(normalized_amount)
            if parsed is None or parsed < Decimal("100"):
                continue
            candidates.append((parsed, match.group(1)))

    if not candidates:
        return None

    _, raw_value = max(candidates, key=lambda item: item[0])
    return raw_value


def provider_from_document_header(text: str) -> str | None:
    limit = RECEIPT_OR_INVOICE_PROVIDER_LIMIT_PATTERN.search(text)
    header = text[: limit.start()] if limit else text[:300]
    for raw_line in header.splitlines():
        candidate = clean_provider_candidate(raw_line)
        if is_probable_provider_name(candidate):
            return candidate
    return None


def normalize_provider_ocr(value: str) -> str:
    normalized = value.replace("$", "S")
    normalized = normalized.replace("IVIA", "MA")
    return normalized


def clean_provider_candidate(value: str) -> str:
    candidate = normalize_provider_ocr(clean_line_value(value))
    candidate = re.sub(r"^(?:[il1]NG\.?|INGENIER[O0])\s+", "", candidate, flags=re.IGNORECASE)
    candidate = re.sub(r"^[^A-Za-zÁÉÍÓÚÑáéíóúñ]+", "", candidate)
    candidate = re.sub(r"^\d{1,3}\s+(?=[A-Za-zÁÉÍÓÚÑáéíóúñ])", "", candidate)
    candidate = re.sub(
        r"^\d{1,3}\s*[-–]\s*\d{1,3}\s+(?=[A-Za-zÁÉÍÓÚÑáéíóúñ])",
        "",
        candidate,
    )
    candidate = re.sub(r"^[a-z]\s+(?=[A-ZÁÉÍÓÚÑ])", "", candidate)
    stop = re.search(
        r"\b(?:TIPO\s+DE\s+PROCESO|CCI|RESPONSABLE|FACTURA|INGENIER[O0]|ABOGAD[O0]|BACH\.?|JR\.|AV\.|CALLE|PCH|AEE|TRB\.?|AMB\.?)\b",
        candidate,
        re.IGNORECASE,
    )
    if stop and stop.start() > 0:
        candidate = candidate[: stop.start()]
    return clean_line_value(candidate)


def is_probable_provider_name(value: str) -> bool:
    if not value or len(value) < 8 or len(value) > 120:
        return False
    normalized = normalize_text(value)
    blocked = (
        "municipalidad",
        "recibi de",
        "telefono",
        "domicilio",
        "direccion",
        "fecha",
        "factura",
        "recibo",
        "puede verificarla",
        "clave sol",
        "representacion impresa",
        "solicito",
        "conformidad de pago",
        "anexo",
        "copia de",
        "orden de servicio",
        "suspension",
        "constancia",
        "dni",
        "segundo",
        "el servicio se",
        "servicio se realizara",
        "actividades que se realizaron",
        "control del cumplimiento",
        "en calidad de",
        "mantenimiento de vias",
        "obras publicas",
        "sub gerencia",
        "subgerencia",
        "costanera",
        "auxiliares",
        "alcredito",
        "sesquicentenario",
        "jr.",
        "av.",
        "calle",
        "nro",
    )
    if any(item in normalized for item in blocked):
        return False
    ignored_name_tokens = {"de", "del", "la", "el", "los", "las", "ia"}
    tokens = [
        token
        for token in normalized.split()
        if len(token) > 1 and token not in ignored_name_tokens
    ]
    corporate_suffixes = {"sac", "eirl", "srl", "sa", "corp", "corporacion", "empresa"}
    if len(tokens) < 3 and not any(token in corporate_suffixes for token in tokens):
        return False
    letter_count = sum(1 for char in value if char.isalpha())
    if letter_count < 6:
        return False
    return bool(re.search(r"[A-Za-z][A-Za-z\s.&'-]{6,}", value))


def clean_line_field(field: str, value: str) -> str:
    cleaned = clean_line_value(value)
    if field == "proveedor":
        cleaned = clean_provider_candidate(cleaned)
    earliest_stop: int | None = None
    for stop_pattern in LINE_FIELD_STOP_PATTERNS.get(field, ()):
        stop = re.search(stop_pattern, cleaned, re.IGNORECASE)
        if stop and stop.start() > 0:
            earliest_stop = (
                stop.start()
                if earliest_stop is None
                else min(earliest_stop, stop.start())
            )

    if earliest_stop is not None:
        cleaned = cleaned[:earliest_stop]

    cleaned = clean_line_value(cleaned)
    if field == "proveedor" and not is_probable_provider_name(cleaned):
        return ""
    if field in {"concepto", "descripcion_servicio"}:
        cleaned = re.sub(
            r"\s+\d{1,6}(?:,\d{3})*\.\d{2}\s+\d+\.\d{2}\s+",
            " ",
            cleaned,
        )
        cleaned = re.sub(
            r"\s+\d+(?:[.,]\d+)+\s+\d+(?:[.,]\d+)+\s+",
            " ",
            cleaned,
        )
        cleaned = re.sub(r"\bSub\s*$", "", cleaned, flags=re.IGNORECASE).strip()
        service_start = re.search(
            r"\bSERVICIO\s+(?:DE|T[E\u00c9]CNICO|TECNICO)\b",
            cleaned,
            re.IGNORECASE,
        )
        if service_start and service_start.start() > 0:
            cleaned = clean_line_value(cleaned[service_start.start() :])
        if is_noise_concept_or_description(cleaned):
            return ""

    max_length = LINE_FIELD_MAX_LENGTH.get(field)
    if max_length and len(cleaned) > max_length:
        cleaned = cleaned[:max_length].rsplit(" ", 1)[0]
        cleaned = clean_line_value(cleaned)
    return cleaned


def is_noise_concept_or_description(value: str) -> bool:
    normalized = normalize_text(value)
    if not normalized or len(normalized) < 6:
        return True
    blocked_prefixes = (
        "total s",
        "totals",
        "referencia",
        "afectacion presupuestal",
        "meta cadena",
        "forma de pago",
        "lugar y plazo",
        "codigo",
        "unid med",
    )
    if normalized.startswith(blocked_prefixes):
        return True
    if normalized in {"total", "total s", "total s/"}:
        return True
    return False


def split_segment_pages(segment: DocumentSegment) -> list[DocumentSegment]:
    page_count = segment.page_end - segment.page_start + 1
    if page_count <= 1:
        return [segment]

    chunks = [chunk.strip() for chunk in segment.text.split("\n\n")]
    if len(chunks) != page_count or any(not chunk for chunk in chunks):
        return [segment]

    return [
        DocumentSegment(
            document_type=segment.document_type,
            page_start=segment.page_start + index,
            page_end=segment.page_start + index,
            text=chunk,
            confidence=segment.confidence,
            evidence=segment.evidence,
        )
        for index, chunk in enumerate(chunks)
    ]


def deduplicate_fields(fields: list[ExtractedDatum]) -> list[ExtractedDatum]:
    seen: set[tuple[str, str, str, int]] = set()
    unique: list[ExtractedDatum] = []
    for field in fields:
        key = (field.field, field.normalized_value, field.source, field.page)
        if key in seen:
            continue
        seen.add(key)
        unique.append(field)
    return unique


def remove_single_source_os_outliers(fields: list[ExtractedDatum]) -> list[ExtractedDatum]:
    os_fields = fields_by_field(fields, "numero_orden_servicio")
    if len(os_fields) <= 1:
        return fields

    grouped: dict[str, list[ExtractedDatum]] = {}
    for field in os_fields:
        grouped.setdefault(comparable_identifier(field.normalized_value), []).append(field)
    if len(grouped) <= 1:
        return fields

    def support_score(item: tuple[str, list[ExtractedDatum]]) -> tuple[int, int]:
        _, candidates = item
        return (len({candidate.source for candidate in candidates}), len(candidates))

    dominant_value, dominant_candidates = max(grouped.items(), key=support_score)
    if len({candidate.source for candidate in dominant_candidates}) < 2 and len(dominant_candidates) < 2:
        return fields

    discarded_values = {
        value
        for value, candidates in grouped.items()
        if value != dominant_value
        and len(candidates) == 1
        and candidates[0].source == "orden_servicio"
    }
    if not discarded_values:
        return fields
    discarded_pages = {
        (candidate.source, candidate.page)
        for value, candidates in grouped.items()
        if value in discarded_values
        for candidate in candidates
    }

    return [
        field
        for field in fields
        if (field.source, field.page) not in discarded_pages
    ]


def remove_single_ruc_ocr_outliers(fields: list[ExtractedDatum]) -> list[ExtractedDatum]:
    ruc_fields = fields_by_field(fields, "ruc")
    if len(ruc_fields) <= 1:
        return fields

    grouped: dict[str, list[ExtractedDatum]] = {}
    for field in ruc_fields:
        grouped.setdefault(field.normalized_value, []).append(field)
    if len(grouped) <= 1:
        return fields

    def support_score(item: tuple[str, list[ExtractedDatum]]) -> tuple[int, int]:
        _, candidates = item
        return (len({candidate.source for candidate in candidates}), len(candidates))

    dominant_value, dominant_candidates = max(grouped.items(), key=support_score)
    if len({candidate.source for candidate in dominant_candidates}) < 2 and len(dominant_candidates) < 2:
        return fields

    discarded_values = {
        value
        for value, candidates in grouped.items()
        if value != dominant_value
        and len(candidates) == 1
        and one_digit_apart(value, dominant_value)
    }
    if not discarded_values:
        return fields

    return [
        field
        for field in fields
        if field.field != "ruc" or field.normalized_value not in discarded_values
    ]


def comparable_identifier(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    return digits.lstrip("0") or "0"


def one_digit_apart(left: str, right: str) -> bool:
    if len(left) != len(right):
        return False
    return sum(left_char != right_char for left_char, right_char in zip(left, right)) == 1


def ensure_description_from_concept(fields: list[ExtractedDatum]) -> list[ExtractedDatum]:
    if fields_by_field(fields, "descripcion_servicio"):
        return fields
    concept = next((field for field in fields if field.field == "concepto"), None)
    if concept is None:
        return fields
    return [
        *fields,
        ExtractedDatum(
            field="descripcion_servicio",
            value=concept.value,
            normalized_value=concept.normalized_value,
            source=concept.source,
            page=concept.page,
            confidence=min(concept.confidence, 0.72),
            evidence=concept.evidence,
            method=concept.method,
        ),
    ]


def ensure_concept_from_description(fields: list[ExtractedDatum]) -> list[ExtractedDatum]:
    if fields_by_field(fields, "concepto"):
        return fields
    description = next((field for field in fields if field.field == "descripcion_servicio"), None)
    if description is None:
        return fields
    return [
        *fields,
        ExtractedDatum(
            field="concepto",
            value=description.value,
            normalized_value=description.normalized_value,
            source=description.source,
            page=description.page,
            confidence=min(description.confidence, 0.72),
            evidence=description.evidence,
            method=description.method,
        ),
    ]
