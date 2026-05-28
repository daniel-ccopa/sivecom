from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent if BACKEND_ROOT.name == "backend" else BACKEND_ROOT


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        populate_by_name=True,
        extra="ignore",
    )

    app_name: str = Field(default="SIVECOM API", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    app_env: str = Field(default="local", alias="APP_ENV")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")

    database_url: str = Field(
        default="postgresql://sivecom:sivecom@localhost:5432/sivecom",
        alias="DATABASE_URL",
    )
    cors_origins_raw: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        alias="CORS_ORIGINS",
    )
    cors_origin_regex: str | None = Field(
        default=r"^http://(localhost|127\.0\.0\.1|192\.168\.[0-9]+\.[0-9]+):5173$",
        alias="CORS_ORIGIN_REGEX",
    )
    upload_dir: Path = Field(default=Path("storage/uploads"), alias="UPLOAD_DIR")
    metadata_dir: Path = Field(default=Path("storage/metadata"), alias="METADATA_DIR")
    text_extraction_dir: Path = Field(
        default=Path("storage/text_extractions"), alias="TEXT_EXTRACTION_DIR"
    )
    segmentation_dir: Path = Field(
        default=Path("storage/segmentations"), alias="SEGMENTATION_DIR"
    )
    data_extraction_dir: Path = Field(
        default=Path("storage/data_extractions"), alias="DATA_EXTRACTION_DIR"
    )
    validation_dir: Path = Field(
        default=Path("storage/validations"), alias="VALIDATION_DIR"
    )
    max_upload_mb: int = Field(default=50, alias="MAX_UPLOAD_MB")
    ocr_language: str = Field(default="es", alias="OCR_LANGUAGE")
    ocr_dpi: int = Field(default=200, alias="OCR_DPI")
    paddle_ocr_base_dir: Path = Field(
        default=Path("storage/paddleocr_models"),
        alias="PADDLE_OCR_BASE_DIR",
    )
    paddle_use_gpu: bool = Field(default=False, alias="PADDLE_USE_GPU")
    paddle_use_textline_orientation: bool = Field(
        default=False,
        alias="PADDLE_USE_TEXTLINE_ORIENTATION",
    )

    @field_validator(
        "upload_dir",
        "metadata_dir",
        "text_extraction_dir",
        "segmentation_dir",
        "data_extraction_dir",
        "validation_dir",
        "paddle_ocr_base_dir",
    )
    @classmethod
    def resolve_project_path(cls, value: Path) -> Path:
        if value.is_absolute():
            return value
        return PROJECT_ROOT / value

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins_raw.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
