"""
FastAPI application entry point.
Defines HTTP endpoints for file storage and AI assistant.
"""

from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, File, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.core.logger import logger
from app.core.schemas import AiData, FileData, FilesResponse
from app.core.settings import settings
from app.core.startup import initialize_rag, rag_service
from app.services.assistant import assistant_service
from app.services.storage import storage_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Runs startup logic before accepting requests, cleanup on shutdown.
    """
    logger.info("Starting Knowledge Hub API...")
    await initialize_rag()
    logger.info("✓ Application ready to accept requests")

    yield

    logger.info("🛑 Shutting down Knowledge Hub API...")


app = FastAPI(
    title="AI Knowledge Hub API",
    lifespan=lifespan,
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.client_url.rstrip("/")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info(f"CORS enabled for: {settings.client_url}")


# ============================================================================
# AI ASSISTANT ENDPOINTS
# ============================================================================


@app.post("/ai")
async def get_ai_answer(data: AiData):
    """Answer a question using RAG + LLM."""
    logger.info(f"[POST /ai] Question received: '{data.question[:50]}...'")

    try:
        answer_text = await assistant_service.answer_question(data.question)
        logger.info("✓ Answer generated successfully")
        return {"status": "success", "answer": answer_text}
    except Exception as e:
        logger.error(f"✗ Error in /ai endpoint: {e}")
        raise


# ============================================================================
# FILE STORAGE ENDPOINTS
# ============================================================================


@app.post("/storage/create")
async def create_file(data: FileData):
    """Create a new file and ingest into RAG."""
    logger.info(f"[POST /storage/create] Creating: {data.filename}")

    try:
        result = storage_service.create_file(data.filename, data.content)
        rag_service.ingest_files(data.filename)

        logger.info(f"✓ File created and ingested: {data.filename}")
        return {"status": "success", "detail": result}
    except Exception as e:
        logger.error(f"✗ Error creating file {data.filename}: {e}")
        raise


@app.put("/storage/edit")
async def edit_file(data: FileData):
    """Edit existing file and re-ingest into RAG."""
    logger.info(f"[PUT /storage/edit] Editing: {data.filename}")

    try:
        result = storage_service.edit_file(data.filename, data.content)
        rag_service.ingest_files(data.filename)

        logger.info(f"✓ File edited and re-ingested: {data.filename}")
        return {"status": "success", "detail": result}
    except Exception as e:
        logger.error(f"✗ Error editing file {data.filename}: {e}")
        raise


@app.post("/storage/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload file from client and ingest into RAG."""
    logger.info(f"[POST /storage/upload] Uploading: {file.filename}")

    try:
        result = storage_service.upload_file_from_pc(file.file, file.filename)

        if result["status"] == "success":
            rag_service.ingest_files(result["filename"])
            logger.info(f"✓ File uploaded and ingested: {result['filename']}")
        else:
            logger.error(f"✗ Upload failed: {result}")

        return result
    except Exception as e:
        logger.error(f"✗ Error uploading file {file.filename}: {e}")
        raise


@app.delete("/storage/delete")
async def delete_file(filename: Annotated[str, Query(...)]):
    """Delete file from filesystem and remove from RAG."""
    logger.info(f"[DELETE /storage/delete] Deleting: {filename}")

    try:
        result = storage_service.delete_file(filename)

        if result["status"] == "deleted":
            rag_service.remove_file_chunks(filename)
            logger.info(f"✓ File deleted from storage and RAG: {filename}")
        else:
            logger.warning(f"⚠ Delete failed: {result}")

        return result
    except Exception as e:
        logger.error(f"✗ Error deleting file {filename}: {e}")
        raise


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================


@app.get("/storage/files", response_model=FilesResponse)
async def list_files():
    """List all files in storage."""
    logger.debug("[GET /storage/files] Listing files")

    try:
        files = storage_service.get_all_files()
        logger.debug(f"✓ Found {len(files)} files")
        return FilesResponse(files=files)
    except Exception as e:
        logger.error(f"✗ Error listing files: {e}")
        raise


@app.get("/storage/content")
async def file_content(filename: Annotated[str, Query(...)]):
    """Get content of a specific file."""
    logger.debug(f"[GET /storage/content] Reading: {filename}")

    try:
        content = storage_service.get_file_content(filename)

        if content is None:
            logger.warning(f"⚠ File not found: {filename}")
        else:
            logger.debug(f"✓ File read: {filename} ({len(content)} chars)")

        return {"filename": filename, "content": content}
    except Exception as e:
        logger.error(f"✗ Error reading file {filename}: {e}")
        raise
