"""Local file storage abstraction."""
import os
import re
import uuid
from pathlib import Path

from app.core.config import get_settings
from app.core.exceptions import FileStorageError
from app.core.logging import get_logger

logger = get_logger("storage")


class LocalStorage:
    """Local filesystem storage for uploaded files."""

    def __init__(self):
        self.base_dir = Path(get_settings().UPLOAD_DIR)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize a filename to prevent path traversal and invalid chars."""
        filename = os.path.basename(filename)
        filename = re.sub(r'[^\w\s\-.]', '', filename)
        if not filename:
            filename = f"file_{uuid.uuid4().hex[:8]}"
        return filename

    def _project_dir(self, project_id: uuid.UUID) -> Path:
        """Get directory for a specific project."""
        return self.base_dir / str(project_id)

    def save(self, project_id: uuid.UUID, filename: str, content: bytes) -> str:
        """Save file content and return the relative storage path.

        Returns:
            Relative path from the base upload directory (e.g., '{project_id}/{filename}')
        """
        safe_filename = self._sanitize_filename(filename)
        project_dir = self._project_dir(project_id)
        project_dir.mkdir(parents=True, exist_ok=True)

        file_path = project_dir / safe_filename
        if file_path.exists():
            stem = file_path.stem
            suffix = file_path.suffix
            safe_filename = f"{stem}_{uuid.uuid4().hex[:8]}{suffix}"
            file_path = project_dir / safe_filename

        try:
            file_path.write_bytes(content)
            logger.info("File saved", extra={
                "operation": "file_save",
                "project_id": str(project_id),
                "detail": safe_filename,
            })
            return f"{project_id}/{safe_filename}"
        except OSError as e:
            raise FileStorageError(
                message="Failed to save file",
                detail=str(e),
            )

    def read(self, relative_path: str) -> bytes:
        """Read file content by relative path."""
        file_path = self.base_dir / relative_path
        try:
            file_path = file_path.resolve()
            base_resolved = self.base_dir.resolve()
            if not str(file_path).startswith(str(base_resolved)):
                raise FileStorageError(
                    message="Invalid file path",
                    detail="Path traversal detected",
                )
        except OSError as e:
            raise FileStorageError(message="Invalid file path", detail=str(e))

        if not file_path.exists():
            raise FileStorageError(
                message="File not found",
                detail=f"File at '{relative_path}' does not exist",
            )
        try:
            return file_path.read_bytes()
        except OSError as e:
            raise FileStorageError(message="Failed to read file", detail=str(e))

    def read_text(self, relative_path: str) -> str:
        """Read file as text."""
        content = self.read(relative_path)
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return content.decode("latin-1")

    def delete(self, relative_path: str) -> None:
        """Delete a file by relative path."""
        file_path = self.base_dir / relative_path
        try:
            file_path = file_path.resolve()
            base_resolved = self.base_dir.resolve()
            if not str(file_path).startswith(str(base_resolved)):
                raise FileStorageError(
                    message="Invalid file path",
                    detail="Path traversal detected",
                )
            if file_path.exists():
                file_path.unlink()
        except OSError as e:
            raise FileStorageError(message="Failed to delete file", detail=str(e))


local_storage = LocalStorage()
