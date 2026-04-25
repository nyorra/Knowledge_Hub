from pathlib import Path

from ..Settings import settings


"""Временное локальное хранилище, в будущем будет на сервере. Путь задается в профиле либо env и не будет хардкодом"""

class FileStorageService:
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path) 
        self._ensure_storage_exist()

    def _ensure_storage_exist(self):
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _get_path(self, filename: str) -> Path:
        return self.storage_path / filename

    def get_all_files(self) -> list[str]:
        return [f.name for f in self.storage_path.iterdir() if f.is_file()]

    def create_file(self, filename: str, content: str):
        file_path = self._get_path(filename)
        file_path.write_text(content, encoding="utf-8")
        return {"status": "created", "filename": filename}

    def get_file_content(self, filename: str):
        try:
            return self._get_path(filename).read_text(encoding="utf-8")
        except FileNotFoundError:
            return None

    def edit_file(self, filename: str, new_content: str):
        file_path = self._get_path(filename)
        if not file_path.exists():
            return {"status": "error", "message": "File not found"}
        file_path.write_text(new_content, encoding="utf-8")
        return {"status": "edited", "filename": filename}

    def delete_file(self, filename: str):
        try:
            self._get_path(filename).unlink()
            return {"status": "deleted", "filename": filename}
        except FileNotFoundError:
            return {"status": "error", "message": "File not found"}



storage_service = FileStorageService(settings.storage_path)

print("--- START TESTING ---")

# 1. CREATE: Создаем базовый файл
print("1. Create:", storage_service.create_file("test.txt", "BEBRA FIRST CONTENT"))

# 2. READ: Проверяем, что записалось
print("2. Read:", storage_service.get_file_content("test.txt"))

# 3. EDIT: Перезаписываем содержимое
print("3. Edit:", storage_service.edit_file("test.txt", "NEW BEBRA IN TEST"))

# 4. READ AGAIN: Проверяем изменения
print("4. Read Update:", storage_service.get_file_content("test.txt"))

# 5. LIST: Смотрим список всех файлов
print("5. All Files:", storage_service.get_all_files())

# 6. DELETE: Удаляем подопытный файл
print("6. Delete:", storage_service.delete_file("test.txt"))

# 7. FINAL CHECK: Проверяем, что файла больше нет
print("7. List after delete:", storage_service.get_all_files())

print("--- END TESTING ---")
