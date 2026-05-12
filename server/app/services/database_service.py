"""
Database service for file and query management.
Provides high-level operations on database models.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.core.models import File, Query, QueryFile


class DatabaseService:
    """Service for database operations."""

    @staticmethod
    async def create_file_record(
        db: AsyncSession,
        filename: str,
        original_filename: str,
        file_path: str,
        file_size: int,
        file_type: str,
        owner_id: Optional[int] = None,
    ) -> File:
        """Create a new file record in database."""
        file_record = File(
            filename=filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            owner_id=owner_id,
        )

        db.add(file_record)
        await db.commit()
        await db.refresh(file_record)

        logger.info(f"✓ File record created: {filename} (ID: {file_record.id})")
        return file_record

    @staticmethod
    async def update_file_indexing(
        db: AsyncSession,
        file_id: int,
        chunk_count: int,
        language: Optional[str] = None,
        char_count: Optional[int] = None,
        page_count: Optional[int] = None,
        error: Optional[str] = None,
    ):
        """Update file record after RAG indexing."""
        result = await db.execute(select(File).where(File.id == file_id))
        file_record = result.scalar_one_or_none()

        if not file_record:
            logger.error(f"✗ File record not found: ID {file_id}")
            return

        file_record.chunk_count = chunk_count
        file_record.is_indexed = error is None
        file_record.indexing_error = error
        file_record.language = language
        file_record.char_count = char_count
        file_record.page_count = page_count

        await db.commit()
        logger.info(
            f"✓ File indexing updated: {file_record.filename} ({chunk_count} chunks)"
        )

    @staticmethod
    async def get_file_by_filename(db: AsyncSession, filename: str) -> Optional[File]:
        """Get file record by filename."""
        result = await db.execute(
            select(File).where(File.filename == filename, File.is_deleted == False)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def soft_delete_file(db: AsyncSession, filename: str) -> bool:
        """Soft delete a file (mark as deleted, don't remove)."""
        file_record = await DatabaseService.get_file_by_filename(db, filename)

        if not file_record:
            return False

        file_record.is_deleted = True
        file_record.deleted_at = datetime.utcnow()
        await db.commit()

        logger.info(f"✓ File soft-deleted: {filename}")
        return True

    @staticmethod
    async def create_query_record(
        db: AsyncSession,
        question: str,
        answer: str,
        response_time_ms: float,
        chunks_retrieved: int,
        source_file_ids: list[int],
        user_id: Optional[int] = None,
    ) -> Query:
        """Create a query record with source files."""
        query_record = Query(
            question=question,
            answer=answer,
            response_time_ms=response_time_ms,
            chunks_retrieved=chunks_retrieved,
            user_id=user_id,
        )

        db.add(query_record)
        await db.flush()  # Get query ID before adding associations

        # Link source files
        for file_id in source_file_ids:
            query_file = QueryFile(query_id=query_record.id, file_id=file_id)
            db.add(query_file)

        await db.commit()
        await db.refresh(query_record)

        logger.info(f"✓ Query record created: ID {query_record.id}")
        return query_record

    @staticmethod
    async def get_analytics(db: AsyncSession) -> dict:
        """Get system analytics."""
        # Total files
        total_files = await db.scalar(
            select(func.count(File.id)).where(File.is_deleted == False)
        )

        # Total queries
        total_queries = await db.scalar(select(func.count(Query.id)))

        # Total chunks
        total_chunks = (
            await db.scalar(
                select(func.sum(File.chunk_count)).where(File.is_deleted == False)
            )
            or 0
        )

        # Average response time
        avg_response_time = await db.scalar(select(func.avg(Query.response_time_ms)))

        return {
            "total_files": total_files or 0,
            "total_queries": total_queries or 0,
            "total_chunks": int(total_chunks),
            "avg_response_time_ms": round(avg_response_time, 2)
            if avg_response_time
            else None,
        }


database_service = DatabaseService()
