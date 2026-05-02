from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, File, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.core.schemas import AiData, FileData, FilesResponse
from app.core.settings import settings
from app.core.startup import initialize_rag, rag_service
from app.services.assistant import assistant_service
from app.services.storage import storage_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    await initialize_rag()
    yield


app = FastAPI(title="AI Knowledge Hub API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.client_url.rstrip("/")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/ai")
async def get_ai_answer(data: AiData):
    answer_text = await assistant_service.answer_question(data.question)
    return {"status": "success", "answer": answer_text}


#
# Кнопки в Хранилище
#
@app.post("/storage/create")
async def create_file(data: FileData):
    result = storage_service.create_file(data.filename, data.content)
    rag_service.ingest_files(data.filename)
    return {"status": "success", "detail": result}


@app.put("/storage/edit")
async def edit_file(data: FileData):
    result = storage_service.edit_file(data.filename, data.content)
    # Re-ingest updated file
    rag_service.ingest_files(data.filename)
    return {"status": "success", "detail": result}


@app.post("/storage/upload")
async def upload_file(file: UploadFile = File(...)):
    result = storage_service.upload_file_from_pc(file.file, file.filename)
    if result["status"] == "success":
        rag_service.ingest_files(result["filename"])
    return result


@app.delete("/storage/delete")
async def delete_file(filename: Annotated[str, Query(...)]):
    result = storage_service.delete_file(filename)
    if result["status"] == "deleted":
        rag_service.remove_file_chunks(filename)
    return result


#
# Вспомогательные
#
@app.get("/storage/files", response_model=FilesResponse)
async def list_files():
    return FilesResponse(files=storage_service.get_all_files())


@app.get("/storage/content")
async def file_content(filename: Annotated[str, Query(...)]):
    content = storage_service.get_file_content(filename)
    return {"filename": filename, "content": content}
