import shutil
import uuid
from pathlib import Path

from ..Settings import settings


class FileStorageService:
    def __init__(self, storage_path: str):
        """Инициализация сервиса: конвертирует путь в объект Path и проверяет его наличие."""
        self.storage_path = Path(storage_path)
        self._ensure_storage_exist()

    def _ensure_storage_exist(self):
        """Автоматическое создание папки хранилища (со всеми родительскими папками)."""
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _get_path(self, filename: str) -> Path:
        """Внутренний хелпер для формирования абсолютного пути к файлу внутри хранилища."""
        return self.storage_path / filename

    def create_file(self, filename: str, content: str):
        """Создает новый текстовый файл (или перезаписывает существующий) с заданным текстом."""
        file_path = self._get_path(filename)
        file_path.write_text(content, encoding="utf-8")
        return {"status": "created", "filename": filename}

    def upload_file_from_pc(
        self, file_object, raw_filename: str, use_uuid: bool = False
    ):
        """
        Сохраняет файл, полученный через веб-запрос, на диск.
        Использует потоковую запись (shutil) для минимизации нагрузки на RAM.
        """
        safe_filename = Path(raw_filename).name

        if use_uuid:
            unique_name = f"{uuid.uuid4().hex[:8]}_{safe_filename}"
        else:
            unique_name = safe_filename

        dest = self._get_path(unique_name)

        try:
            with dest.open("wb") as buffer:
                shutil.copyfileobj(file_object, buffer)
            return {"status": "success", "filename": unique_name}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_all_files(self) -> list[str]:
        """Возвращает плоский список имен всех файлов, находящихся в корне хранилища."""
        return [f.name for f in self.storage_path.iterdir() if f.is_file()]

    def get_file_content(self, filename: str):
        """Читает и возвращает содержимое текстового файла. Возвращает None, если файл отсутствует."""
        try:
            return self._get_path(filename).read_text(encoding="utf-8")
        except FileNotFoundError:
            return None

    def edit_file(self, filename: str, new_content: str):
        """Перезаписывает содержимое существующего файла. Возвращает ошибку, если файла нет."""
        file_path = self._get_path(filename)
        if not file_path.exists():
            return {"status": "error", "message": "File not found"}
        file_path.write_text(new_content, encoding="utf-8")
        return {"status": "edited", "filename": filename}

    def delete_file(self, filename: str):
        """Физическое удаление файла с диска. Обрабатывает исключение отсутствия файла."""
        try:
            self._get_path(filename).unlink()
            return {"status": "deleted", "filename": filename}
        except FileNotFoundError:
            return {"status": "error", "message": "File not found"}


# Инициализация глобального экземпляра сервиса
storage_service = FileStorageService(settings.storage_path)
