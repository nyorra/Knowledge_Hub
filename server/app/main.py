"""
FastAPI application entry point.
Defines HTTP endpoints for file storage and AI assistant.
"""

import time
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logger import logger
from app.core.schemas import AiData, FileData, FilesResponse
from app.core.settings import settings
from app.core.startup import initialize_rag, rag_service
from app.services.assistant import assistant_service
from app.services.database_service import database_service
from app.services.storage import storage_service
from app.services.transcription import transcription_service


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
async def get_ai_answer(data: AiData, db: AsyncSession = Depends(get_db)):
    """Answer a question using RAG + LLM."""
    logger.info(f"[POST /ai] Question received: '{data.question[:50]}...'")
    start_time = time.time()

    try:
        answer_text = await assistant_service.answer_question(data.question)
        elapsed_ms = (time.time() - start_time) * 1000

        # Track query in database (optional, can be disabled)
        try:
            # Get source files from the answer context (simplified)
            await database_service.create_query_record(
                db=db,
                question=data.question,
                answer=answer_text,
                response_time_ms=elapsed_ms,
                chunks_retrieved=5,  # Default top_k
                source_file_ids=[],  # Would need to track this from RAG
            )
        except Exception as db_error:
            logger.warning(f"Failed to log query to database: {db_error}")

        logger.info(f"✓ Answer generated successfully ({elapsed_ms:.0f}ms)")
        return {"status": "success", "answer": answer_text}

    except Exception as e:
        logger.error(f"✗ Error in /ai endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate answer: {str(e)}",
        )


@app.post("/ai/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe audio file to text using Whisper API."""
    logger.info(f"[POST /ai/transcribe] Transcribing audio: {file.filename}")

    try:
        text = await transcription_service.transcribe_audio(file)
        logger.info(f"✓ Audio transcribed successfully: {len(text)} chars")
        return {"status": "success", "text": text}
    except ValueError as e:
        logger.error(f"✗ Transcription validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"✗ Transcription error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transcription failed",
        )


# ============================================================================
# FILE STORAGE ENDPOINTS
# ============================================================================


@app.post("/storage/create")
async def create_file(data: FileData, db: AsyncSession = Depends(get_db)):
    """Create a new file and ingest into RAG."""
    logger.info(f"[POST /storage/create] Creating: {data.filename}")

    try:
        result = storage_service.create_file(data.filename, data.content)

        # Create database record
        file_path = storage_service._get_path(result["filename"])
        file_size = len(data.content.encode("utf-8"))

        file_record = await database_service.create_file_record(
            db=db,
            filename=result["filename"],
            original_filename=data.filename,
            file_path=str(file_path),
            file_size=file_size,
            file_type=file_path.suffix,
        )

        try:
            ingest_result = await rag_service.ingest_files(data.filename)

            # Update database with indexing results
            await database_service.update_file_indexing(
                db=db,
                file_id=file_record.id,
                chunk_count=ingest_result["chunks_created"],
                language=ingest_result.get("language"),
                char_count=ingest_result.get("char_count"),
                page_count=ingest_result.get("page_count"),
            )

            logger.info(f"✓ File created and ingested: {data.filename}")
            return {"status": "success", "detail": result, "file_id": file_record.id}

        except ValueError as e:
            # Update database with error
            await database_service.update_file_indexing(
                db=db,
                file_id=file_record.id,
                chunk_count=0,
                error=str(e),
            )
            logger.error(f"✗ Parsing error for {data.filename}: {e}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"File created but parsing failed: {str(e)}",
            )

    except ValueError as e:
        logger.error(f"✗ Validation error for {data.filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"✗ Error creating file {data.filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create file",
        )


@app.put("/storage/edit")
async def edit_file(data: FileData, db: AsyncSession = Depends(get_db)):
    """Edit existing file and re-ingest into RAG."""
    logger.info(f"[PUT /storage/edit] Editing: {data.filename}")

    try:
        result = storage_service.edit_file(data.filename, data.content)

        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["message"],
            )

        # Get existing file record
        file_record = await database_service.get_file_by_filename(db, data.filename)

        if not file_record:
            logger.warning(
                f"File exists in storage but not in database: {data.filename}"
            )
            # Create database record if missing
            file_path = storage_service._get_path(data.filename)
            file_size = len(data.content.encode("utf-8"))

            file_record = await database_service.create_file_record(
                db=db,
                filename=data.filename,
                original_filename=data.filename,
                file_path=str(file_path),
                file_size=file_size,
                file_type=file_path.suffix,
            )

        try:
            ingest_result = await rag_service.ingest_files(data.filename)

            # Update database with indexing results
            await database_service.update_file_indexing(
                db=db,
                file_id=file_record.id,
                chunk_count=ingest_result["chunks_created"],
                language=ingest_result.get("language"),
                char_count=ingest_result.get("char_count"),
                page_count=ingest_result.get("page_count"),
            )

            logger.info(f"✓ File edited and re-ingested: {data.filename}")
            return {"status": "success", "detail": result}

        except ValueError as e:
            # Update database with error
            await database_service.update_file_indexing(
                db=db,
                file_id=file_record.id,
                chunk_count=0,
                error=str(e),
            )
            logger.error(f"✗ Parsing error for {data.filename}: {e}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"File edited but parsing failed: {str(e)}",
            )

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"✗ Validation error for {data.filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"✗ Error editing file {data.filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to edit file",
        )


@app.post("/storage/upload")
async def upload_file(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """Upload file from client and ingest into RAG."""
    logger.info(f"[POST /storage/upload] Uploading: {file.filename}")
    start_time = time.time()

    try:
        result = storage_service.upload_file_from_pc(file.file, file.filename)

        if result["status"] == "success":
            # Create database record
            file_path = storage_service._get_path(result["filename"])
            file_size = file_path.stat().st_size

            file_record = await database_service.create_file_record(
                db=db,
                filename=result["filename"],
                original_filename=file.filename,
                file_path=str(file_path),
                file_size=file_size,
                file_type=file_path.suffix,
            )

            try:
                # Ingest into RAG
                ingest_result = await rag_service.ingest_files(result["filename"])

                # Update database with indexing results
                await database_service.update_file_indexing(
                    db=db,
                    file_id=file_record.id,
                    chunk_count=ingest_result["chunks_created"],
                    language=ingest_result.get("language"),
                    char_count=ingest_result.get("char_count"),
                    page_count=ingest_result.get("page_count"),
                )

                elapsed = (time.time() - start_time) * 1000
                logger.info(
                    f"✓ File uploaded and ingested: {result['filename']} ({elapsed:.0f}ms)"
                )
                return {
                    "status": "success",
                    "filename": result["filename"],
                    "file_id": file_record.id,
                }

            except ValueError as e:
                # Update database with error
                await database_service.update_file_indexing(
                    db=db,
                    file_id=file_record.id,
                    chunk_count=0,
                    error=str(e),
                )
                logger.error(f"✗ Parsing error for {result['filename']}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Upload succeeded but parsing failed: {str(e)}",
                )
        else:
            logger.error(f"✗ Upload failed: {result}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("message", "Upload failed"),
            )

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"✗ Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"✗ Error uploading file {file.filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Upload failed",
        )


@app.delete("/storage/delete")
async def delete_file(
    filename: Annotated[str, Query(...)], db: AsyncSession = Depends(get_db)
):
    """Delete file from filesystem and remove from RAG."""
    logger.info(f"[DELETE /storage/delete] Deleting: {filename}")

    try:
        # Soft delete in database first
        db_deleted = await database_service.soft_delete_file(db, filename)

        if not db_deleted:
            logger.warning(f"⚠ File not found in database: {filename}")

        # Remove from filesystem
        result = storage_service.delete_file(filename)

        if result["status"] == "deleted":
            # Remove from RAG
            await rag_service.remove_file_chunks(filename)
            logger.info(f"✓ File deleted from storage and RAG: {filename}")
            return {"status": "deleted", "filename": filename}
        else:
            logger.warning(f"⚠ Delete failed: {result}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("message", "File not found"),
            )

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"✗ Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"✗ Error deleting file {filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file",
        )


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint for monitoring."""
    try:
        # Check database
        analytics = await database_service.get_analytics(db)

        # Check storage
        file_count = len(storage_service.get_all_files())

        return {
            "status": "healthy",
            "database": "connected",
            "vector_store": "connected",
            "chunks_indexed": analytics["total_chunks"],
            "files_stored": file_count,
            "files_in_db": analytics["total_files"],
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy",
        )


@app.get("/analytics")
async def get_analytics(db: AsyncSession = Depends(get_db)):
    """Get system analytics and statistics."""
    logger.info("[GET /analytics] Fetching analytics")

    try:
        analytics = await database_service.get_analytics(db)
        return analytics
    except Exception as e:
        logger.error(f"✗ Error fetching analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch analytics",
        )


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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list files",
        )


@app.get("/storage/content")
async def file_content(filename: Annotated[str, Query(...)]):
    """Get content of a specific file."""
    logger.debug(f"[GET /storage/content] Reading: {filename}")

    try:
        content = storage_service.get_file_content(filename)

        if content is None:
            logger.warning(f"⚠ File not found: {filename}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found",
            )

        logger.debug(f"✓ File read: {filename} ({len(content)} chars)")
        return {"filename": filename, "content": content}

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"✗ Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"✗ Error reading file {filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to read file",
        )
