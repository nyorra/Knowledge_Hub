"""
Application startup logic.
Initializes RAG service and database.
"""

import asyncio

from app.core.database import init_db
from app.core.logger import logger
from app.services.RAG import RAGService

# Global RAG service instance
rag_service = RAGService()
logger.info("✓ RAG service instance created")


async def initialize_rag():
    """Initialize RAG system and database on startup."""
    logger.info("=" * 60)
    logger.info("STARTUP: Initializing system")
    logger.info("=" * 60)

    try:
        # Initialize database
        await init_db()

        # Start background ingestion task
        asyncio.create_task(_background_ingestion())

        logger.info("✓ System initialization complete")
        logger.info("=" * 60)

        return {"status": "started", "message": "Background ingestion in progress"}
    except Exception as e:
        logger.error(f"✗ System initialization failed: {e}")
        raise


async def _background_ingestion():
    """Background task for ingesting all existing files."""
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
