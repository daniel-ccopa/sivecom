import re
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from app.models.document_segment import DocumentSegmentationResult
from app.models.extracted_data import DataExtractionResult, ExtractedDatum
from app.models.validation_result import (
    ValidationEvidence,
    ValidationItem,
    ValidationRun,
)


RESULT_OK = "OK"
RESULT_WARNING = "ADVERTENCIA"
RESULT_ERROR = "ERROR"

SEVERITY_INFO = "info"
SEVERITY_LOW = "baja"
SEVERITY_MEDIUM = "media"
SEVERITY_HIGH = "alta"

TOLERANCE = Decimal("0.05")
LOW_DOCUMENT_CONFIDENCE = 0.35

REQUIRED_DOCUMENTS = {
    "carta_solicitud": "carta de solicitud",
    "orden_servicio": "orden de servicio",
    "informe_actividades": "informe de actividades",
    "recibo_honorarios": "comprobante de pago (recibo por honorarios o factura)",
}

CORE_FIELDS = {
    "numero_orden_servicio": "numero de orden de servicio",
    "ruc": "RUC del proveedor",
    "proveedor": "nombre o razon social del proveedor",
    "monto_total_os": "monto total de la O/S",
    "monto_entregable": "monto del entregable o comprobante",
    "concepto": "concepto",
    "descripcion_servicio": "descripcion del servicio",
}

@dataclass(frozen=True)
class ValidationContext:
    segmentation: DocumentSegmentationResult
    extraction: DataExtractionResult
    previous_extractions: list[DataExtractionResult]


class ValidationRule:
    rule_id: str = ""
    tipo: str = ""
    affected_fields: list[str] = []

    def evaluate(self, context: ValidationContext) -> ValidationItem:
        raise NotImplementedError

    def item(
        self,
        resultado: str,
        severidad: str,
        mensaje: str,
        evidencia: list[ValidationEvidence],
        recomendacion: str,
        affected_fields: list[str] | None = None,
    ) -> ValidationItem:
        return ValidationItem(
            rule_id=self.rule_id,
            tipo=self.tipo,
            resultado=resultado,
            severidad=severidad,
            mensaje=mensaje,
            evidencia=evidencia,
            recomendacion=recomendacion,
            passed=resultado == RESULT_OK,
            affected_fields=affected_fields or self.affected_fields,
        )


class CoreFieldsPresenceRule(ValidationRule):
    rule_id = "R001"
    tipo = "campos_principales_detectados"
    affected_fields = list(CORE_FIELDS)

    def evaluate(self, context: ValidationContext) -> ValidationItem:
        present = {field.field for field in context.extraction.fields}
        required = set(CORE_FIELDS)
        missing = sorted(required - present)

        evidence = key_evidence(context.extraction)

        if missing:
            labels = [f"{CORE_FIELDS[field_name]} ({field_name})" for field_name in missing]
            present_labels = [
                f"{CORE_FIELDS[field.field]} en {field.source} pag. {field.page}"
                for field in context.extraction.fields
                if field.field in CORE_FIELDS
            ]
            return self.item(
                RESULT_WARNING,
                SEVERITY_MEDIUM,
                (
                    f"Faltan campos principales: {', '.join(labels)}. "
                    f"Detectados: {', '.join(present_labels) if present_labels else 'ninguno'}."
                ),
                evidence,
                "Revisar las paginas de los documentos obligatorios y confirmar manualmente los campos faltantes.",
                affected_fields=missing,
            )

        return self.item(
            RESULT_OK,
            SEVERITY_INFO,
            "Los datos principales solicitados fueron detectados.",
            evidence,
            "Continuar con la revision administrativa.",
        )


class OSNumberConsistencyRule(ValidationRule):
    rule_id = "R002"
    tipo = "coincidencia_numero_orden_servicio"
    affected_fields = ["numero_orden_servicio"]

    def evaluate(self, context: ValidationContext) -> ValidationItem:
        fields = fields_by_name(context.extraction, "numero_orden_servicio")
        evidence = field_evidence(fields)
        if not fields:
            return self.item(
                RESULT_WARNING,
                SEVERITY_MEDIUM,
                "No se encontro numero de orden de servicio.",
                evidence,
                "Verificar manualmente el numero de O/S.",
            )

        comparable_values = {
            comparable_identifier(field.normalized_value)
            for field in fields
            if field.normalized_value
        }
        display_values = display_values_by_comparable_identifier(fields)
        if len(comparable_values) > 1:
            return self.item(
                RESULT_WARNING,
                SEVERITY_HIGH,
                "Se detectaron numeros de orden de servicio diferentes.",
                evidence,
                "Contrastar manualmente la O/S antes de continuar.",
            )

        return self.item(
            RESULT_OK,
            SEVERITY_INFO,
            f"El numero de orden de servicio detectado es consistente: {', '.join(display_values)}.",
            evidence,
            "Continuar revision.",
        )


class RUCConsistencyRule(ValidationRule):
    rule_id = "R003"
    tipo = "coincidencia_ruc"
    affected_fields = ["ruc"]

    def evaluate(self, context: ValidationContext) -> ValidationItem:
        fields = fields_by_name(context.extraction, "ruc")
        evidence = field_evidence(fields)
        if not fields:
            return self.item(
                RESULT_WARNING,
                SEVERITY_MEDIUM,
                "No se encontro RUC del proveedor.",
                evidence,
                "Verificar manualmente el RUC.",
            )

        invalid = [
            field for field in fields if not re.fullmatch(r"\d{11}", field.normalized_value)
        ]
        if invalid:
            return self.item(
                RESULT_WARNING,
                SEVERITY_HIGH,
                "Se detecto un RUC con formato invalido.",
                field_evidence(invalid),
                "Revisar el RUC en el expediente.",
            )

        unique_values = {field.normalized_value for field in fields}
        if len(unique_values) > 1:
            return self.item(
                RESULT_WARNING,
                SEVERITY_HIGH,
                "El RUC aparece con valores diferentes.",
                evidence,
                "Contrastar manualmente el RUC del proveedor.",
            )

        return self.item(
            RESULT_OK,
            SEVERITY_INFO,
            "El RUC detectado es consistente en los documentos donde aparece.",
            evidence,
            "Continuar revision.",
        )


class AmountConsistencyRule(ValidationRule):
    rule_id = "R004"
    tipo = "revision_montos"
    affected_fields = ["monto_total_os", "monto_entregable"]

    def evaluate(self, context: ValidationContext) -> ValidationItem:
        os_amounts = parsed_amounts(context.extraction, "monto_total_os")
        deliverable_amounts = parsed_amounts(context.extraction, "monto_entregable")
        evidence = field_evidence(
            fields_by_name(context.extraction, "monto_total_os")
            + fields_by_name(context.extraction, "monto_entregable")
        )

        if not os_amounts and not deliverable_amounts:
            return self.item(
                RESULT_WARNING,
                SEVERITY_MEDIUM,
                "No se detectaron montos suficientes para comparar.",
                evidence,
                "Revisar manualmente monto de O/S y monto del entregable.",
            )

        if os_amounts and deliverable_amounts:
            os_total = max(os_amounts)
            deliverable_total = max(deliverable_amounts)
            if deliverable_total > os_total + TOLERANCE:
                return self.item(
                    RESULT_ERROR,
                    SEVERITY_HIGH,
                    "El monto del entregable supera el monto total de la O/S.",
                    evidence,
                    "Revisar montos antes de emitir conformidad.",
                )

        return self.item(
            RESULT_OK,
            SEVERITY_INFO,
            "Los montos principales no presentan inconsistencias: el comprobante no supera la O/S.",
            evidence,
            "Continuar revision.",
        )


class DeliverableScheduleAmountRule(ValidationRule):
    rule_id = "R008"
    tipo = "cronograma_entregables"
    affected_fields = [
        "numero_entregables",
        "porcentaje_entregable",
        "monto_total_os",
        "monto_entregable",
    ]

    def evaluate(self, context: ValidationContext) -> ValidationItem:
        count_fields = fields_by_name(context.extraction, "numero_entregables")
        percent_fields = fields_by_name(context.extraction, "porcentaje_entregable")
        os_amount_fields = fields_by_name(context.extraction, "monto_total_os")
        deliverable_amount_fields = fields_by_name(context.extraction, "monto_entregable")
        evidence = field_evidence(
            count_fields + percent_fields + os_amount_fields + deliverable_amount_fields
        )

        if not count_fields and not percent_fields:
            return self.item(
                RESULT_OK,
                SEVERITY_INFO,
                "No se detecto cronograma de entregables en la O/S; se mantiene la validacion general de montos.",
                evidence,
                "Continuar revision.",
            )

        os_amounts = unique_parsed_amounts(os_amount_fields)
        deliverable_amounts = unique_parsed_amounts(deliverable_amount_fields)
        if not os_amounts or not deliverable_amounts:
            return self.item(
                RESULT_WARNING,
                SEVERITY_LOW,
                "Se detecto cronograma de entregables, pero faltan montos suficientes para compararlo.",
                evidence,
                "Revisar manualmente el monto total de la O/S y el comprobante del entregable.",
            )

        os_total = max(os_amounts)
        count = parsed_deliverable_count(count_fields)
        schedule = deliverable_percentages(percent_fields)

        if schedule:
            if count is not None and len(schedule) != count:
                return self.item(
                    RESULT_WARNING,
                    SEVERITY_LOW,
                    (
                        f"La O/S indica {count} entregable(s), pero se detectaron "
                        f"{len(schedule)} porcentaje(s) de entregable."
                    ),
                    evidence,
                    "Revisar si el OCR omitio algun porcentaje del cronograma de pago.",
                )

            percent_total = sum(schedule.values())
            if abs(percent_total - Decimal("100")) > Decimal("1"):
                return self.item(
                    RESULT_WARNING,
                    SEVERITY_MEDIUM,
                    f"Los porcentajes de entregables suman {format_decimal(percent_total)}%, no 100%.",
                    evidence,
                    "Revisar el cronograma de pago de la orden de servicio.",
                )

            expected_amounts = [
                money_round(os_total * percent / Decimal("100"))
                for percent in schedule.values()
            ]
            unmatched = [
                amount
                for amount in deliverable_amounts
                if not any(abs(amount - expected) <= TOLERANCE for expected in expected_amounts)
            ]
            if unmatched:
                expected_text = ", ".join(format_money_value(amount) for amount in expected_amounts)
                found_text = ", ".join(format_money_value(amount) for amount in deliverable_amounts)
                return self.item(
                    RESULT_WARNING,
                    SEVERITY_HIGH,
                    (
                        "El monto del comprobante no coincide con los montos programados "
                        f"por entregable. Esperado segun O/S: {expected_text}. Detectado: {found_text}."
                    ),
                    evidence,
                    "Contrastar manualmente el entregable, porcentaje y comprobante antes de emitir conformidad.",
                )

            return self.item(
                RESULT_OK,
                SEVERITY_INFO,
                "El monto del comprobante coincide con el cronograma de entregables de la O/S.",
                evidence,
                "Continuar revision.",
            )

        if count == 1:
            deliverable_total = max(deliverable_amounts)
            if abs(deliverable_total - os_total) > TOLERANCE:
                return self.item(
                    RESULT_WARNING,
                    SEVERITY_HIGH,
                    (
                        "La O/S indica un unico entregable, pero el monto del comprobante "
                        "no coincide con el monto total de la O/S."
                    ),
                    evidence,
                    "Revisar si el expediente corresponde a un pago parcial o si falta algun comprobante.",
                )

        return self.item(
            RESULT_OK,
            SEVERITY_INFO,
            "Se detecto cronograma de entregables sin conflictos de monto verificables.",
            evidence,
            "Continuar revision.",
        )


class ServiceDescriptionRule(ValidationRule):
    rule_id = "R005"
    tipo = "concepto_y_descripcion"
    affected_fields = ["concepto", "descripcion_servicio"]

    def evaluate(self, context: ValidationContext) -> ValidationItem:
        fields = (
            fields_by_name(context.extraction, "concepto")
            + fields_by_name(context.extraction, "descripcion_servicio")
        )
        evidence = field_evidence(fields)
        present = {field.field for field in fields}
        missing = [
            field_name
            for field_name in self.affected_fields
            if field_name not in present
        ]
        if missing:
            labels = ", ".join(CORE_FIELDS[field_name] for field_name in missing)
            return self.item(
                RESULT_WARNING,
                SEVERITY_LOW,
                f"Falta detalle textual de: {labels}.",
                evidence,
                "Revisar manualmente el texto del servicio o informe si es necesario.",
                affected_fields=missing,
            )

        return self.item(
            RESULT_OK,
            SEVERITY_INFO,
            "Concepto y descripcion fueron detectados.",
            evidence,
            "Continuar revision.",
        )


class ProviderConsistencyRule(ValidationRule):
    rule_id = "R006"
    tipo = "coincidencia_proveedor"
    affected_fields = ["proveedor"]

    def evaluate(self, context: ValidationContext) -> ValidationItem:
        fields = fields_by_name(context.extraction, "proveedor")
        evidence = field_evidence(fields)
        if not fields:
            return self.item(
                RESULT_WARNING,
                SEVERITY_MEDIUM,
                "No se encontro nombre o razon social del proveedor para comparar.",
                evidence,
                "Revisar manualmente el proveedor en carta, O/S y comprobante.",
            )

        unique_values = unique_normalized_values(fields)
        if len(unique_values) <= 1:
            return self.item(
                RESULT_OK,
                SEVERITY_INFO,
                "El proveedor detectado no presenta conflictos.",
                evidence,
                "Continuar revision.",
            )

        base = unique_values[0]
        conflicts = [
            value for value in unique_values[1:] if token_similarity(base, value) < 0.55
        ]
        if conflicts:
            return self.item(
                RESULT_WARNING,
                SEVERITY_HIGH,
                "Se detectaron nombres de proveedor con baja coincidencia entre documentos.",
                evidence,
                "Contrastar manualmente la razon social del proveedor antes de continuar.",
            )

        return self.item(
            RESULT_OK,
            SEVERITY_INFO,
            "Los nombres de proveedor detectados son compatibles entre documentos.",
            evidence,
            "Continuar revision.",
        )


class ServiceTextCoherenceRule(ValidationRule):
    rule_id = "R007"
    tipo = "coherencia_servicio"
    affected_fields = ["concepto", "descripcion_servicio"]

    def evaluate(self, context: ValidationContext) -> ValidationItem:
        fields = (
            fields_by_name(context.extraction, "concepto")
            + fields_by_name(context.extraction, "descripcion_servicio")
        )
        evidence = field_evidence(fields)
        by_source: dict[str, str] = {}
        for field in fields:
            value = field.normalized_value or field.value
            if is_delivery_label(value):
                continue
            by_source.setdefault(field.source, value)

        if len(by_source) <= 1:
            present = documents_present(context.segmentation)
            all_required_documents = all(document_type in present for document_type in REQUIRED_DOCUMENTS)
            if "orden_servicio" in by_source and all_required_documents:
                return self.item(
                    RESULT_OK,
                    SEVERITY_INFO,
                    "El servicio fue detectado en la orden de servicio y no hay texto contradictorio en otros documentos.",
                    evidence,
                    "Continuar revision, verificando visualmente si el expediente lo requiere.",
                )
            return self.item(
                RESULT_WARNING,
                SEVERITY_LOW,
                "Solo se encontro texto del servicio en un documento; no hay suficiente informacion para comparar.",
                evidence,
                "Revisar manualmente que el informe y el recibo correspondan al servicio contratado.",
            )

        sources = list(by_source.items())
        base_source, base_value = sources[0]
        low_matches = [
            source
            for source, value in sources[1:]
            if token_similarity(base_value, value) < 0.25
        ]
        if low_matches:
            return self.item(
                RESULT_WARNING,
                SEVERITY_MEDIUM,
                (
                    "El texto del servicio no coincide claramente entre documentos. "
                    f"Documento base: {base_source}; revisar: {', '.join(low_matches)}."
                ),
                evidence,
                "Comparar manualmente concepto de O/S, informe y comprobante de pago.",
            )

        return self.item(
            RESULT_OK,
            SEVERITY_INFO,
            "El concepto o descripcion del servicio mantiene coincidencia textual entre documentos.",
            evidence,
            "Continuar revision.",
        )


class RequiredDocumentsRule(ValidationRule):
    rule_id = "R000"
    tipo = "documentos_obligatorios"
    affected_fields = list(REQUIRED_DOCUMENTS)

    def evaluate(self, context: ValidationContext) -> ValidationItem:
        present = documents_present(context.segmentation)
        missing = [
            document_type
            for document_type in REQUIRED_DOCUMENTS
            if document_type not in present
        ]
        low_confidence = [
            document_type
            for document_type, confidence in present.items()
            if document_type in REQUIRED_DOCUMENTS and confidence < LOW_DOCUMENT_CONFIDENCE
        ]

        evidence = document_evidence(context.segmentation, REQUIRED_DOCUMENTS)
        if missing:
            labels = [REQUIRED_DOCUMENTS[document_type] for document_type in missing]
            detected = [
                f"{REQUIRED_DOCUMENTS[document_type]} pag. {pages_for_document(context.segmentation, document_type)}"
                for document_type in REQUIRED_DOCUMENTS
                if document_type in present
            ]
            return self.item(
                RESULT_ERROR,
                SEVERITY_HIGH,
                (
                    f"No se detectaron documentos obligatorios: {', '.join(labels)}. "
                    f"Detectados: {', '.join(detected) if detected else 'ninguno'}."
                ),
                evidence,
                "Solicitar subsanacion o revisar manualmente si el OCR no pudo reconocer el documento.",
                affected_fields=missing,
            )

        if low_confidence:
            labels = [REQUIRED_DOCUMENTS[document_type] for document_type in low_confidence]
            return self.item(
                RESULT_WARNING,
                SEVERITY_MEDIUM,
                f"Todos los documentos obligatorios aparecen, pero con baja confianza: {', '.join(labels)}.",
                evidence,
                "Revisar visualmente las paginas marcadas antes de emitir conformidad.",
                affected_fields=low_confidence,
            )

        return self.item(
            RESULT_OK,
            SEVERITY_INFO,
            "Se detectaron los 4 documentos obligatorios: carta, orden de servicio, informe y comprobante de pago.",
            evidence,
            "Continuar con la comparacion de datos extraidos.",
        )


class ValidationEngine:
    def __init__(self, rules: list[ValidationRule] | None = None) -> None:
        self.rules = rules or [
            RequiredDocumentsRule(),
            CoreFieldsPresenceRule(),
            OSNumberConsistencyRule(),
            RUCConsistencyRule(),
            AmountConsistencyRule(),
            DeliverableScheduleAmountRule(),
            ServiceDescriptionRule(),
            ProviderConsistencyRule(),
            ServiceTextCoherenceRule(),
        ]

    def evaluate(
        self,
        segmentation: DocumentSegmentationResult,
        extraction: DataExtractionResult,
        previous_extractions: list[DataExtractionResult] | None = None,
    ) -> ValidationRun:
        context = ValidationContext(
            segmentation=segmentation,
            extraction=extraction,
            previous_extractions=previous_extractions or [],
        )
        validations = [rule.evaluate(context) for rule in self.rules]
        return ValidationRun(
            expediente_id=segmentation.expediente_id,
            verdict=build_verdict(validations),
            summary=build_summary(validations),
            validations=validations,
            validated_at=datetime.now(timezone.utc),
        )


def fields_by_name(extraction: DataExtractionResult, field_name: str) -> list[ExtractedDatum]:
    return [field for field in extraction.fields if field.field == field_name]


def parsed_amounts(extraction: DataExtractionResult, field_name: str) -> list[Decimal]:
    values: list[Decimal] = []
    for field in fields_by_name(extraction, field_name):
        parsed = parse_decimal(field.normalized_value)
        if parsed is not None:
            values.append(parsed)
    return values


def unique_parsed_amounts(fields: list[ExtractedDatum]) -> list[Decimal]:
    values: list[Decimal] = []
    for field in fields:
        parsed = parse_decimal(field.normalized_value)
        if parsed is not None and parsed not in values:
            values.append(parsed)
    return values


def parse_decimal(value: str) -> Decimal | None:
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return None


def parsed_deliverable_count(fields: list[ExtractedDatum]) -> int | None:
    counts: list[int] = []
    for field in fields:
        try:
            counts.append(int(field.normalized_value))
        except ValueError:
            continue
    return max(counts) if counts else None


def deliverable_percentages(fields: list[ExtractedDatum]) -> dict[int, Decimal]:
    schedule: dict[int, Decimal] = {}
    for field in fields:
        match = re.fullmatch(r"(\d+):(\d+(?:\.\d+)?)", field.normalized_value)
        if not match:
            continue
        ordinal = int(match.group(1))
        percent = Decimal(match.group(2))
        schedule.setdefault(ordinal, percent)
    return dict(sorted(schedule.items()))


def money_round(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"))


def format_decimal(value: Decimal) -> str:
    return f"{value.normalize():f}"


def format_money_value(value: Decimal) -> str:
    return f"S/ {value.quantize(Decimal('0.01'))}"


def field_evidence(fields: list[ExtractedDatum]) -> list[ValidationEvidence]:
    return [
        ValidationEvidence(
            text=safe_evidence_text(field.evidence or field.value),
            page=field.page,
            document_type=field.source,
            field=field.field,
        )
        for field in fields
    ]


def key_evidence(extraction: DataExtractionResult) -> list[ValidationEvidence]:
    evidence = []
    for field_name in CORE_FIELDS:
        evidence.extend(field_evidence(fields_by_name(extraction, field_name)[:1]))
    return evidence


def documents_present(segmentation: DocumentSegmentationResult) -> dict[str, float]:
    present: dict[str, float] = {}
    for segment in segmentation.segments:
        if segment.document_type == "desconocido":
            continue
        document_type = (
            "recibo_honorarios"
            if segment.document_type == "factura"
            else segment.document_type
        )
        present[document_type] = max(
            present.get(document_type, 0.0),
            segment.confidence,
        )
    return present


def pages_for_document(segmentation: DocumentSegmentationResult, document_type: str) -> str:
    accepted_types = {document_type}
    if document_type == "recibo_honorarios":
        accepted_types.add("factura")
    pages = [
        str(segment.page_start)
        if segment.page_start == segment.page_end
        else f"{segment.page_start}-{segment.page_end}"
        for segment in segmentation.segments
        if segment.document_type in accepted_types
    ]
    return ", ".join(pages) if pages else "-"


def document_evidence(
    segmentation: DocumentSegmentationResult,
    document_labels: dict[str, str],
) -> list[ValidationEvidence]:
    evidence: list[ValidationEvidence] = []
    for segment in segmentation.segments:
        document_type = (
            "recibo_honorarios"
            if segment.document_type == "factura"
            else segment.document_type
        )
        if document_type not in document_labels:
            continue
        evidence_text = ", ".join(segment.evidence) or document_labels[document_type]
        evidence.append(
            ValidationEvidence(
                text=safe_evidence_text(evidence_text),
                page=segment.page_start,
                document_type=segment.document_type,
                field=document_type,
            )
        )
    return evidence


def safe_evidence_text(value: str, max_length: int = 160) -> str:
    compact = re.sub(r"\s+", " ", value).strip()
    masked = re.sub(r"\b(\d{2})\d{7}(\d{2})\b", r"\1*******\2", compact)
    return masked[:max_length]


def unique_normalized_values(fields: list[ExtractedDatum]) -> list[str]:
    values: list[str] = []
    for field in fields:
        value = normalize_for_comparison(field.normalized_value or field.value)
        if value and value not in values:
            values.append(value)
    return values


def normalize_for_comparison(value: str) -> str:
    clean = re.sub(r"[^a-z0-9\s]", " ", value.lower())
    return re.sub(r"\s+", " ", clean).strip()


def comparable_identifier(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    return digits.lstrip("0") or "0"


def display_values_by_comparable_identifier(fields: list[ExtractedDatum]) -> list[str]:
    display: dict[str, str] = {}
    for field in fields:
        if not field.normalized_value:
            continue
        key = comparable_identifier(field.normalized_value)
        current = display.get(key)
        if current is None or len(field.normalized_value) > len(current):
            display[key] = field.normalized_value
    return sorted(display.values())


def token_similarity(left: str, right: str) -> float:
    left_tokens = comparable_tokens(left)
    right_tokens = comparable_tokens(right)
    if not left_tokens or not right_tokens:
        return 0.0
    intersection = left_tokens.intersection(right_tokens)
    union = left_tokens.union(right_tokens)
    return len(intersection) / len(union)


def comparable_tokens(value: str) -> set[str]:
    stopwords = {
        "de",
        "del",
        "la",
        "el",
        "los",
        "las",
        "para",
        "por",
        "sac",
        "s",
        "a",
        "c",
        "eirl",
        "empresa",
        "servicio",
        "servicios",
        "segun",
        "orden",
        "numero",
        "nro",
    }
    return {
        normalize_service_token(token)
        for token in normalize_for_comparison(value).split()
        if len(token) > 2 and not token.isdigit() and token not in stopwords
    }


def normalize_service_token(token: str) -> str:
    replacements = {
        "servlclct": "servicio",
        "servlclo": "servicio",
        "serviclo": "servicio",
        "responsabm": "responsable",
        "tecnlco": "tecnico",
        "subgerencla": "subgerencia",
        "publca": "publicas",
        "publcas": "publicas",
        "14antenimieni0": "mantenimiento",
        "mantenimient0": "mantenimiento",
        "mantenimeinto": "mantenimiento",
        "mantenimeint0": "mantenimiento",
    }
    if token in replacements:
        return replacements[token]
    token = re.sub(r"^\d+", "", token.replace("0", "o"))
    if len(token) > 5 and token.endswith("ion"):
        return token[:-1]
    return token


def is_delivery_label(value: str) -> bool:
    normalized = normalize_for_comparison(value)
    return (
        ("entregable" in normalized and "servicio" not in normalized)
        or normalized.startswith("solicito conformidad")
        or "conformidad de pago" in normalized
        or "tramite de conformidad" in normalized
        or "conformidad para el pago" in normalized
    )


def build_summary(validations: list[ValidationItem]) -> dict[str, int]:
    return {
        "ok": sum(1 for item in validations if item.resultado == RESULT_OK),
        "advertencias": sum(1 for item in validations if item.resultado == RESULT_WARNING),
        "errores": sum(1 for item in validations if item.resultado == RESULT_ERROR),
        "criticas": 0,
    }


def build_verdict(validations: list[ValidationItem]) -> str:
    if any(item.resultado == RESULT_ERROR for item in validations):
        return "rechazar"
    if any(item.resultado == RESULT_WARNING for item in validations):
        return "revision_manual"
    return "procede_conformidad"
