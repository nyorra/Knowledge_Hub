from typing import Annotated

from fastapi import FastAPI, File, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# Импортируем явно, чтобы линтер не ругался
from app.schemas import AskRequest, AskResponse, FileData, FilesResponse
from app.services.storage import storage_service
from app.Settings import settings

app = FastAPI(title="AI Knowledge Hub API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.client_url.rstrip("/")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/ask", response_model=AskResponse)
async def get_ai_request(data: AskRequest):
    return AskResponse(status="success", answer=f"Получено: {data.text}")


# Кнопки в Хранилище
@app.post("/storage/create")
async def create_file(data: FileData):
    # Если storage_service.create_file синхронный,
    # FastAPI сам вынесет его в threadpool, но лучше сделать его async
    result = storage_service.create_file(data.filename, data.content)
    return {"status": "success", "detail": result}


@app.put("/storage/edit")
async def edit_file(data: FileData):
    result = storage_service.edit_file(data.filename, data.content)
    return {"status": "success", "detail": result}


@app.post("/storage/upload")
async def upload_file(file: UploadFile = File(...)):
    # Используем await, если сервис асинхронный
    return storage_service.upload_file_from_pc(file.file, file.filename)


@app.delete("/storage/delete")
async def delete_file(filename: Annotated[str, Query(...)]):
    return storage_service.delete_file(filename)


# Вспомогательные
@app.get("/storage/files", response_model=FilesResponse)
async def list_files():
    return FilesResponse(files=storage_service.get_all_files())


@app.get("/storage/content")
async def file_content(filename: Annotated[str, Query(...)]):
    content = storage_service.get_file_content(filename)
    return {"filename": filename, "content": content}
