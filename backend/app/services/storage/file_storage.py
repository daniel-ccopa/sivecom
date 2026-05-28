from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status


PDF_SIGNATURE = b"%PDF-"
ALLOWED_CONTENT_TYPES = {"application/pdf", "application/x-pdf", "application/octet-stream"}


@dataclass(frozen=True)
class SavedFile:
    original_filename: str
    stored_filename: str
    size_bytes: int
    sha256: str
    content_type: str | None


class FileStorageService:
    def __init__(self, upload_dir: Path, max_upload_mb: int) -> None:
        self.upload_dir = upload_dir
        self.max_upload_bytes = max_upload_mb * 1024 * 1024

    def save_pdf(self, file: UploadFile) -> SavedFile:
        self._validate_pdf_metadata(file)
        self._validate_pdf_signature(file)

        self.upload_dir.mkdir(parents=True, exist_ok=True)
        original_filename = Path(file.filename or "expediente.pdf").name
        stored_filename = f"{uuid4().hex}.pdf"
        target_path = self.upload_dir / stored_filename

        digest = sha256()
        total_size = 0
        try:
            with target_path.open("wb") as output:
                while chunk := file.file.read(1024 * 1024):
                    total_size += len(chunk)
                    if total_size > self.max_upload_bytes:
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail="El PDF supera el tamano maximo permitido.",
                        )
                    digest.update(chunk)
                    output.write(chunk)
        except Exception:
            target_path.unlink(missing_ok=True)
            raise

        return SavedFile(
            original_filename=original_filename,
            stored_filename=stored_filename,
            size_bytes=total_size,
            sha256=digest.hexdigest(),
            content_type=file.content_type,
        )

    def _validate_pdf_metadata(self, file: UploadFile) -> None:
        filename = file.filename or ""
        content_type = file.content_type or ""
        if not filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se permiten archivos con extension .pdf.",
            )
        if content_type and content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El tipo MIME del archivo no es PDF.",
            )

    def _validate_pdf_signature(self, file: UploadFile) -> None:
        file.file.seek(0)
        header = file.file.read(len(PDF_SIGNATURE))
        file.file.seek(0)
        if header != PDF_SIGNATURE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El contenido del archivo no corresponde a un PDF.",
            )
