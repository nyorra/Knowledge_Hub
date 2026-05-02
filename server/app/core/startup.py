"""
Application startup logic.
Initializes RAG service and ingests existing files on server start.
"""

from app.core.logger import logger
from app.services.RAG import RAGService

# Global RAG service instance (initialized once, used throughout app lifecycle)
rag_service = RAGService()
logger.info("✓ RAG service instance created")


async def initialize_rag():
    logger.info("=" * 60)
    logger.info("STARTUP: Initializing RAG system")
    logger.info("=" * 60)

    try:
        result = rag_service.ingest_all_files()

        logger.info("✓ RAG initialization complete")
        logger.info(f"  Files processed: {result['files_processed']}")
        logger.info(f"  Total chunks created: {result['total_chunks']}")
        logger.info("=" * 60)

        return result
    except Exception as e:
        logger.error(f"✗ RAG initialization failed: {e}")
        raise
