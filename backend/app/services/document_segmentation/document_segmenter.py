import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone

from app.models.document_segment import DocumentSegment, DocumentSegmentationResult
from app.models.text_extraction import ExtractedPageText, TextExtractionResult


@dataclass(frozen=True)
class KeywordRule:
    pattern: str
    evidence: str
    weight: float = 1.0


@dataclass(frozen=True)
class PageClassification:
    page_number: int
    document_type: str
    confidence: float
    evidence: list[str]
    text: str


DOCUMENT_RULES: dict[str, tuple[KeywordRule, ...]] = {
    "carta_solicitud": (
        KeywordRule(r"\bcarta\b", "carta", 2.0),
        KeywordRule(r"\bcarta\s+n", "carta numero", 4.0),
        KeywordRule(r"\bpara\s*:", "para", 1.5),
        KeywordRule(r"\bde\s*:", "de", 1.5),
        KeywordRule(r"\bsolicito\b", "solicito", 2.0),
        KeywordRule(r"\bconformidad\b", "conformidad", 2.0),
        KeywordRule(r"servicio realizado", "servicio realizado", 2.0),
        KeywordRule(r"\badjunto\b", "adjunto"),
        KeywordRule(r"\batentamente\b", "atentamente"),
        KeywordRule(r"\bsubgerencia\b", "subgerencia"),
        KeywordRule(r"\bmunicipalidad\b", "municipalidad"),
    ),
    "orden_servicio": (
        KeywordRule(r"orden de servicio", "orden de servicio", 4.0),
        KeywordRule(r"orden\s+de\s+serv[l1]c[l1]o", "orden de servicio OCR", 4.0),
        KeywordRule(r"orden\s+que\s+se.*contratacion\s+de\s+serv", "orden que se emite", 3.0),
        KeywordRule(r"exp\.?\s*siaf|expediente\s*siaf", "exp. siaf", 2.0),
        KeywordRule(r"condiciones generales", "condiciones generales", 2.0),
        KeywordRule(r"datos del proveedor", "datos del proveedor", 2.0),
        KeywordRule(r"modulo\s+de\s+logistica|m[o0]dulo\s+de\s+log", "modulo de logistica", 2.0),
        KeywordRule(r"ordenacion\s+del\s+servicio", "ordenacion del servicio", 2.0),
        KeywordRule(r"d[e8]scripc\w*n\s+servicios\s+diversos", "descripcion servicios diversos", 2.0),
        KeywordRule(r"afectacion presupuestal", "afectacion presupuestal", 2.0),
        KeywordRule(r"afec\w*cion\s+presu", "afectacion presupuestal OCR", 2.0),
        KeywordRule(r"unidad\s+ejecutora|umdad\s+e\.?ecutora", "unidad ejecutora", 2.0),
        KeywordRule(r"nro\.?\s+identificaci[o0]n|wro\.?\s+i?deunficaci[o0]n", "nro identificacion", 2.0),
        KeywordRule(r"forma\s+de\s+pago|fora\s+de\s+paco", "forma de pago", 1.5),
        KeywordRule(r"monto total", "monto total"),
        KeywordRule(r"\bigv\b", "igv"),
        KeywordRule(r"\bvalor\b", "valor"),
    ),
    "recibo_honorarios": (
        KeywordRule(r"recibo por honorarios", "recibo por honorarios", 4.0),
        KeywordRule(r"recibo\s+por\s+l[i1]o?norarios", "recibo por honorarios OCR", 4.0),
        KeywordRule(r"recibo\s+po[ftr]\s+[i1l]?[i1l]?[h1l]ono\w+", "recibo por honorarios OCR fuerte", 4.0),
        KeywordRule(r"recibo\s+po[ftr].{0,20}electronico", "recibo electronico OCR", 4.0),
        KeywordRule(r"honorarios\s+electronico|honoraries", "honorarios electronico OCR", 3.0),
        KeywordRule(r"total\s+(?:por\s+)?honorarios", "total honorarios", 2.0),
        KeywordRule(r"total\s+p[o0][rt]\s+honorar\w+", "total honorarios OCR", 2.0),
        KeywordRule(r"\bretencion\b", "retencion", 2.0),
        KeywordRule(r"\brotencl6n\b|\brotenclon\b", "retencion OCR", 2.0),
        KeywordRule(r"total neto recibido", "total neto recibido", 2.0),
        KeywordRule(r"total\s+nato\s+roc[i1l]b[i1l]do", "total neto recibido OCR", 2.0),
        KeywordRule(r"informacion del credito", "informacion del credito"),
        KeywordRule(r"informacl[o0]n\s+d[o0]l\s+cr[e6]d[i1l]to", "informacion del credito OCR"),
        KeywordRule(r"fecha de emision", "fecha de emision"),
        KeywordRule(r"fochadeem[i1l]sl[o0]n", "fecha de emision OCR"),
    ),
    "factura": (
        KeywordRule(r"factura electronica", "factura electronica", 4.0),
        KeywordRule(r"\bfactura\b", "factura", 3.0),
        KeywordRule(r"\bruc\b", "ruc"),
        KeywordRule(r"\bigv\b", "igv"),
        KeywordRule(r"valor venta", "valor venta", 2.0),
        KeywordRule(r"importe total", "importe total", 2.0),
        KeywordRule(r"fecha de emision", "fecha de emision"),
    ),
    "informe_actividades": (
        KeywordRule(r"acta\s+de\s+entrega", "acta de entrega", 5.0),
        KeywordRule(r"se\s+deja\s+constancia", "constancia de entrega", 2.5),
        KeywordRule(r"entrega\s+del\s+servicio|servicio\s+se\s+entrega", "entrega del servicio", 2.5),
        KeywordRule(r"quien\s+entrega", "quien entrega", 1.5),
        KeywordRule(r"quien\s+recibe", "quien recibe", 1.5),
        KeywordRule(r"\binforme\b", "informe", 2.0),
        KeywordRule(r"\basunto\b", "asunto"),
        KeywordRule(r"\breferencia\b", "referencia"),
        KeywordRule(r"\bantecedentes\b", "antecedentes", 2.0),
        KeywordRule(r"\banalisis\b", "analisis", 2.0),
        KeywordRule(r"actividades realizadas", "actividades realizadas", 3.0),
        KeywordRule(r"\bconclusiones\b", "conclusiones", 2.0),
        KeywordRule(r"\brecomendaciones\b", "recomendaciones", 2.0),
    ),
    "anexo_fotografico": (
        KeywordRule(r"\banexo\b", "anexo", 2.0),
        KeywordRule(r"\bfotografias?\b", "fotografias", 2.0),
        KeywordRule(r"registro fotografico", "registro fotografico", 3.0),
        KeywordRule(r"evidencia fotografica", "evidencia fotografica", 3.0),
        KeywordRule(r"\bimagen\b", "imagen"),
    ),
}


class DocumentSegmenter:
    def __init__(self, min_confidence: float = 0.25) -> None:
        self.min_confidence = min_confidence

    def segment(self, text_result: TextExtractionResult) -> DocumentSegmentationResult:
        classifications = [
            self.classify_page(page)
            for page in sorted(text_result.pages, key=lambda item: item.page_number)
        ]
        segments = self._add_embedded_informe_segments(self._group_pages(classifications))
        status = (
            "segmentado"
            if any(segment.document_type != "desconocido" for segment in segments)
            else "sin_segmentos"
        )
        return DocumentSegmentationResult(
            expediente_id=text_result.expediente_id,
            status=status,
            segments=segments,
            segmented_at=datetime.now(timezone.utc),
        )

    def classify_page(self, page: ExtractedPageText) -> PageClassification:
        normalized_text = normalize_text(page.text)
        if not normalized_text:
            return PageClassification(
                page_number=page.page_number,
                document_type="desconocido",
                confidence=0.0,
                evidence=[],
                text=page.text,
            )

        scored = [
            self._score_document_type(document_type, rules, normalized_text)
            for document_type, rules in DOCUMENT_RULES.items()
        ]
        scored = self._apply_document_type_adjustments(scored, normalized_text)
        best_type, best_score, best_confidence, best_evidence = max(
            scored,
            key=lambda item: (item[1], item[2], len(item[3])),
        )

        if best_score <= 0 or best_confidence < self.min_confidence:
            best_type = "desconocido"
            best_confidence = 0.0
            best_evidence = []

        return PageClassification(
            page_number=page.page_number,
            document_type=best_type,
            confidence=best_confidence,
            evidence=best_evidence,
            text=page.text,
        )

    def _score_document_type(
        self,
        document_type: str,
        rules: tuple[KeywordRule, ...],
        normalized_text: str,
    ) -> tuple[str, float, float, list[str]]:
        score = 0.0
        evidence: list[str] = []
        for rule in rules:
            if re.search(rule.pattern, normalized_text):
                score += rule.weight
                evidence.append(rule.evidence)

        max_score = sum(rule.weight for rule in rules)
        confidence_denominator = min(max_score, 8.0)
        confidence = (
            round(min(1.0, score / confidence_denominator), 2)
            if confidence_denominator
            else 0.0
        )
        return document_type, score, confidence, evidence

    @staticmethod
    def _apply_document_type_adjustments(
        scored: list[tuple[str, float, float, list[str]]],
        normalized_text: str,
    ) -> list[tuple[str, float, float, list[str]]]:
        adjusted: list[tuple[str, float, float, list[str]]] = []
        looks_like_formal_letter = bool(
            re.search(r"\bcarta\s+n", normalized_text)
            and re.search(r"\b(?:para|de|asunto)\s*:", normalized_text)
        )
        for document_type, score, confidence, evidence in scored:
            if document_type == "carta_solicitud" and looks_like_formal_letter:
                score += 3.0
                confidence = min(1.0, round(confidence + 0.2, 2))
                evidence = [*evidence, "estructura de carta"]
            adjusted.append((document_type, score, confidence, evidence))
        return adjusted

    def _group_pages(self, pages: list[PageClassification]) -> list[DocumentSegment]:
        if not pages:
            return []

        segments: list[DocumentSegment] = []
        current = [pages[0]]
        for page in pages[1:]:
            previous = current[-1]
            if (
                page.document_type == previous.document_type
                and page.page_number == previous.page_number + 1
                and should_group_pages(previous, page)
            ):
                current.append(page)
                continue
            segments.append(self._build_segment(current))
            current = [page]

        segments.append(self._build_segment(current))
        return segments

    @staticmethod
    def _add_embedded_informe_segments(
        segments: list[DocumentSegment],
    ) -> list[DocumentSegment]:
        if any(segment.document_type == "informe_actividades" for segment in segments):
            return segments

        enriched = list(segments)
        for segment in segments:
            normalized = normalize_text(segment.text)
            if segment.document_type != "carta_solicitud":
                continue
            if not (
                "informe de actividades" in normalized
                and (
                    "actividades realizadas" in normalized
                    or "labores realizadas" in normalized
                    or "cumplo con informar" in normalized
                )
            ):
                continue
            enriched.append(
                DocumentSegment(
                    document_type="informe_actividades",
                    page_start=segment.page_start,
                    page_end=segment.page_end,
                    text=segment.text,
                    confidence=0.42,
                    evidence=[
                        "informe de actividades",
                        "contenido embebido en carta",
                    ],
                )
            )
            break
        return sorted(enriched, key=lambda item: (item.page_start, item.document_type))

    @staticmethod
    def _build_segment(pages: list[PageClassification]) -> DocumentSegment:
        evidence: list[str] = []
        for page in pages:
            for item in page.evidence:
                if item not in evidence:
                    evidence.append(item)

        confidence = round(sum(page.confidence for page in pages) / len(pages), 2)
        return DocumentSegment(
            document_type=pages[0].document_type,
            page_start=pages[0].page_number,
            page_end=pages[-1].page_number,
            text="\n\n".join(page.text for page in pages).strip(),
            confidence=confidence,
            evidence=evidence,
        )


def normalize_text(value: str) -> str:
    lowered = value.lower()
    without_accents = "".join(
        char
        for char in unicodedata.normalize("NFKD", lowered)
        if not unicodedata.combining(char)
    )
    cleaned = without_accents.replace("\N{DEGREE SIGN}", " ").replace(
        "\N{MASCULINE ORDINAL INDICATOR}",
        " ",
    )
    return re.sub(r"\s+", " ", cleaned).strip()


def should_group_pages(previous: PageClassification, current: PageClassification) -> bool:
    if current.document_type != "orden_servicio":
        return True

    previous_numbers = order_numbers_from_text(previous.text)
    current_numbers = order_numbers_from_text(current.text)
    if previous_numbers and current_numbers and previous_numbers.isdisjoint(current_numbers):
        return False
    return True


ORDER_NUMBER_PATTERN = re.compile(
    r"orden\s+de\s+serv(?:icio|[i1l]c[i1l]o)\s*(?:n|no|nro)?\s*[.:°º\-]?\s*([0-9oocs\s.\-]{4,20})",
    re.IGNORECASE,
)


def order_numbers_from_text(text: str) -> set[str]:
    return {
        normalize_order_number(match.group(1))
        for match in ORDER_NUMBER_PATTERN.finditer(text)
        if normalize_order_number(match.group(1))
    }


def normalize_order_number(value: str) -> str:
    corrected = (
        value.replace("O", "0")
        .replace("o", "0")
        .replace("C", "0")
        .replace("c", "0")
        .replace("S", "5")
        .replace("s", "5")
    )
    digits = re.sub(r"\D", "", corrected)
    if not digits:
        return ""
    year = re.search(r"20\d{2}", digits)
    if year and year.start() >= 6:
        digits = digits[: year.start()]
    if re.search(r"[\s.\-][Oo]\s*$", value) and len(digits) > 6:
        digits = digits[:-1]
    normalized = digits.lstrip("0") or "0"
    return normalized.zfill(6) if len(normalized) <= 6 else normalized
