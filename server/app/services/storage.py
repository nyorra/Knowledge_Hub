"""
File storage service for managing user documents.
Handles CRUD operations on local filesystem.
"""

import shutil
import uuid
from pathlib import Path

from app.core.logger import logger
from app.core.settings import settings


class FileStorageService:
    """
    Service for managing file storage operations.
    All files are stored in a single directory specified by settings.storage_path.
    """

    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self._ensure_storage_exist()
        logger.info(f"✓ FileStorageService initialized at: {self.storage_path}")

    def _ensure_storage_exist(self):
        self.storage_path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Storage directory verified: {self.storage_path}")

    def _get_path(self, filename: str) -> Path:
        return self.storage_path / filename

    def create_file(self, filename: str, content: str):
        logger.info(f"[CREATE] Creating file: {filename}")

        try:
            file_path = self._get_path(filename)
            file_path.write_text(content, encoding="utf-8")

            logger.info(f"✓ File created: {filename} ({len(content)} chars)")
            return {"status": "created", "filename": filename}
        except Exception as e:
            logger.error(f"✗ Failed to create file {filename}: {e}")
            raise

    def upload_file_from_pc(
        self, file_object, raw_filename: str, use_uuid: bool = False
    ):
        safe_filename = Path(raw_filename).name

        if use_uuid:
            unique_name = f"{uuid.uuid4().hex[:8]}_{safe_filename}"
            logger.info(f"[UPLOAD] Uploading with UUID: {unique_name}")
        else:
            unique_name = safe_filename
            logger.info(f"[UPLOAD] Uploading file: {unique_name}")

        dest = self._get_path(unique_name)

        try:
            with dest.open("wb") as buffer:
                shutil.copyfileobj(file_object, buffer)

            file_size = dest.stat().st_size
            logger.info(f"✓ File uploaded: {unique_name} ({file_size} bytes)")
            return {"status": "success", "filename": unique_name}
        except Exception as e:
            logger.error(f"✗ Upload failed for {unique_name}: {e}")
            return {"status": "error", "message": str(e)}

    def get_all_files(self) -> list[str]:
        files = [f.name for f in self.storage_path.iterdir() if f.is_file()]
        logger.debug(f"[LIST] Found {len(files)} files in storage")
        return files

    def get_file_content(self, filename: str):
        logger.debug(f"[READ] Reading file: {filename}")

        try:
            content = self._get_path(filename).read_text(encoding="utf-8")
            logger.debug(f"✓ File read: {filename} ({len(content)} chars)")
            return content
        except FileNotFoundError:
            logger.warning(f"✗ File not found: {filename}")
            return None

    def edit_file(self, filename: str, new_content: str):
        logger.info(f"[EDIT] Editing file: {filename}")

        file_path = self._get_path(filename)
        if not file_path.exists():
            logger.warning(f"✗ Cannot edit - file not found: {filename}")
            return {"status": "error", "message": "File not found"}

        try:
            file_path.write_text(new_content, encoding="utf-8")
            logger.info(f"✓ File edited: {filename} ({len(new_content)} chars)")
            return {"status": "edited", "filename": filename}
        except Exception as e:
            logger.error(f"✗ Edit failed for {filename}: {e}")
            raise

    def delete_file(self, filename: str):
        logger.info(f"[DELETE] Deleting file: {filename}")

        try:
            self._get_path(filename).unlink()
            logger.info(f"✓ File deleted: {filename}")
            return {"status": "deleted", "filename": filename}
        except FileNotFoundError:
            logger.warning(f"✗ Cannot delete - file not found: {filename}")
            return {"status": "error", "message": "File not found"}


storage_service = FileStorageService(settings.storage_path)
