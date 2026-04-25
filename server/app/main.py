from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.Settings import settings
from app.schemas import AskRequest, AskResponse
from app.services.storage import storage_service


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.client_url.rstrip("/")], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask")
async def get_ai_request(data: AskRequest):
    return AskResponse(status="success", answer=f"Получено: {data.text}")


@app.post("/storage/create")
async def create_file(filename: str, content: str):
    return storage_service.create_file(filename, content)

@app.post("/storage/upload")
async def upload_file(file: UploadFile = File(...)):
    return storage_service.upload_file_from_pc(file.file, file.filename)

@app.get("/storage/files")
async def list_files():
    return {"files": storage_service.get_all_files()}

@app.get("/storage/content")
async def file_content(filename: str):
    return {"file content": storage_service.get_file_content(filename)}

@app.put("/storage/edit")
async def edit_file(filename: str, content: str):
    return storage_service.edit_file(filename, content)

@app.delete("/storage/delete")
async def delete_file(filename: str):
    return storage_service.delete_file(filename)