from dataclasses import dataclass
from io import BytesIO
import os
from pathlib import Path
from typing import Any, Protocol


class OcrUnavailableError(RuntimeError):
    pass


@dataclass(frozen=True)
class OcrResult:
    text: str
    confidence: float | None = None


class OcrEngine(Protocol):
    def extract_text(self, image_bytes: bytes) -> OcrResult:
        raise NotImplementedError


class PaddleOcrEngine:
    """Local OCR engine backed by PaddleOCR.

    The PaddleOCR package is imported lazily because the library is heavy and
    downloads local model files on first use.
    """

    def __init__(
        self,
        language: str = "es",
        model_base_dir: Path | None = None,
        use_gpu: bool = False,
        use_textline_orientation: bool = True,
    ) -> None:
        self.language = language
        self.model_base_dir = model_base_dir
        self.use_gpu = use_gpu
        self.use_textline_orientation = use_textline_orientation
        self._engine: Any | None = None

    def extract_text(self, image_bytes: bytes) -> OcrResult:
        try:
            from PIL import Image
            import numpy as np
        except ImportError as exc:
            raise OcrUnavailableError(
                "Las dependencias de imagen requeridas por PaddleOCR no estan disponibles."
            ) from exc

        try:
            image = Image.open(BytesIO(image_bytes)).convert("RGB")
            image_array = np.array(image)
            raw_result = self._run_paddleocr(image_array)
        except OcrUnavailableError:
            raise
        except Exception as exc:
            raise OcrUnavailableError(
                "PaddleOCR no pudo procesar la pagina renderizada."
            ) from exc

        lines = parse_paddle_ocr_result(raw_result)
        text = " ".join(line_text for line_text, _ in lines).strip()
        scores = [score for _, score in lines if score is not None]
        confidence = round(sum(scores) / len(scores), 2) if scores else None
        return OcrResult(text=text, confidence=confidence)

    def _run_paddleocr(self, image_array: Any) -> Any:
        engine = self._get_engine()
        if hasattr(engine, "predict"):
            return engine.predict(image_array)
        return engine.ocr(image_array, cls=self.use_textline_orientation)

    def _get_engine(self) -> Any:
        if self._engine is not None:
            return self._engine

        if self.model_base_dir is not None:
            self.model_base_dir.mkdir(parents=True, exist_ok=True)
            os.environ.setdefault("PADDLE_OCR_BASE_DIR", str(self.model_base_dir))
        os.environ.setdefault("DISABLE_MODEL_SOURCE_CHECK", "True")

        try:
            from paddleocr import PaddleOCR
        except ImportError as exc:
            raise OcrUnavailableError(
                "PaddleOCR no esta instalado. Ejecuta pip install -r backend/requirements.txt."
            ) from exc

        self._engine = self._build_engine(PaddleOCR)
        return self._engine

    def _build_engine(self, paddle_ocr_class: Any) -> Any:
        v3_kwargs = {
            "lang": self.language,
            "use_doc_orientation_classify": False,
            "use_doc_unwarping": False,
            "use_textline_orientation": self.use_textline_orientation,
        }
        for kwargs in (
            {**v3_kwargs, "device": "gpu" if self.use_gpu else "cpu"},
            v3_kwargs,
        ):
            try:
                return paddle_ocr_class(**kwargs)
            except TypeError:
                continue

        return paddle_ocr_class(
            lang=self.language,
            use_gpu=self.use_gpu,
            use_angle_cls=self.use_textline_orientation,
            show_log=False,
        )


def parse_paddle_ocr_result(raw_result: Any) -> list[tuple[str, float | None]]:
    lines: list[tuple[str, float | None]] = []
    for item in ensure_iterable(raw_result):
        lines.extend(extract_mapping_lines(item))
        lines.extend(extract_legacy_lines(item))
    return deduplicate_lines(lines)


def extract_mapping_lines(value: Any) -> list[tuple[str, float | None]]:
    if not isinstance(value, dict):
        return []

    payload = value.get("res", value)
    if not isinstance(payload, dict):
        return []

    texts = first_present(payload, "rec_texts", "texts")
    scores = first_present(payload, "rec_scores", "scores")
    if is_empty_sequence(scores):
        scores = [None] * len(texts)
    return [
        (cleaned, normalize_score(score))
        for text, score in zip(texts, scores, strict=False)
        if (cleaned := str(text).strip())
    ]


def extract_legacy_lines(value: Any) -> list[tuple[str, float | None]]:
    parsed = parse_legacy_line(value)
    if parsed is not None:
        return [parsed]

    if isinstance(value, (list, tuple)):
        lines: list[tuple[str, float | None]] = []
        for item in value:
            lines.extend(extract_legacy_lines(item))
        return lines

    return []


def parse_legacy_line(value: Any) -> tuple[str, float | None] | None:
    if not isinstance(value, (list, tuple)) or len(value) < 2:
        return None

    for candidate in (value[1], value[0]):
        if (
            isinstance(candidate, (list, tuple))
            and len(candidate) >= 2
            and isinstance(candidate[0], str)
        ):
            text = candidate[0].strip()
            if text:
                return text, normalize_score(candidate[1])
    return None


def first_present(payload: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = payload.get(key)
        if value is not None:
            return value
    return []


def is_empty_sequence(value: Any) -> bool:
    try:
        return len(value) == 0
    except TypeError:
        return False


def ensure_iterable(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def normalize_score(value: Any) -> float | None:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return None
    return round(score * 100, 2) if 0 <= score <= 1 else round(score, 2)


def deduplicate_lines(lines: list[tuple[str, float | None]]) -> list[tuple[str, float | None]]:
    seen: set[str] = set()
    unique: list[tuple[str, float | None]] = []
    for text, score in lines:
        if text in seen:
            continue
        seen.add(text)
        unique.append((text, score))
    return unique
