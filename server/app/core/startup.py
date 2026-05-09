"""
Application startup logic.
Initializes RAG service and defers file ingestion to background task.
"""

import asyncio

from app.core.logger import logger
from app.services.RAG import RAGService

# Global RAG service instance (initialized once, used throughout app lifecycle)
rag_service = RAGService()
logger.info("✓ RAG service instance created")


async def initialize_rag():
    """
    Initialize RAG system on startup.
    File ingestion runs in background to avoid blocking server startup.
    """
    logger.info("=" * 60)
    logger.info("STARTUP: Initializing RAG system")
    logger.info("=" * 60)

    try:
        # Start background ingestion task (non-blocking)
        asyncio.create_task(_background_ingestion())

        logger.info("✓ RAG initialization complete (ingestion running in background)")
        logger.info("=" * 60)

        return {"status": "started", "message": "Background ingestion in progress"}
    except Exception as e:
        logger.error(f"✗ RAG initialization failed: {e}")
        raise


async def _background_ingestion():
    """
    Background task for ingesting all existing files.
    Runs after server startup to avoid blocking.
    """
    logger.info("[BACKGROUND] Starting file ingestion...")

    try:
        result = await rag_service.ingest_all_files()

        logger.info("=" * 60)
        logger.info("✓ Background ingestion complete")
        logger.info(f"  Files processed: {result['files_processed']}")
        logger.info(f"  Total chunks created: {result['total_chunks']}")
        if result.get("errors"):
            logger.warning(f"  Errors: {len(result['errors'])} files failed")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"✗ Background ingestion failed: {e}")
