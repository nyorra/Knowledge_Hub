"""
Retrieval-Augmented Generation (RAG) service.
Manages vector embeddings and semantic search for knowledge retrieval.

Architecture:
- Embeddings: sentence-transformers/all-MiniLM-L6-v2 (local, CPU)
- Vector Store: ChromaDB (persistent)
- Chunking: RecursiveCharacterTextSplitter (1000 chars, 200 overlap)
"""

import asyncio
from pathlib import Path

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.logger import logger
from app.services.document_parser import document_parser_service
from app.services.storage import storage_service


class RAGService:
    """
    Service for managing document ingestion and semantic retrieval.
    Uses ChromaDB for persistent vector storage.
    """

    def __init__(self, persist_directory: str = "./chroma_db"):
        logger.info("Initializing RAG service...")

        # 1. Initialize text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""],
        )
        logger.debug("✓ Text splitter configured (1000 chars, 200 overlap)")

        # 2. Initialize embedding model
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
        )
        logger.debug("✓ Embedding model loaded (all-MiniLM-L6-v2)")

        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(exist_ok=True)

        # 3. Initialize ChromaDB vector store
        self.vector_store = Chroma(
            collection_name="knowledge_hub",
            embedding_function=self.embeddings,
            persist_directory=str(self.persist_directory),
        )
        logger.info(f"✓ ChromaDB initialized at: {self.persist_directory}")

    async def ingest_files(self, filename: str):
        """
        Ingest a single file into the vector store (async, non-blocking).

        Raises:
            ValueError: If parsing fails
        """
        logger.info(f"[INGEST] Processing file: {filename}")

        # 1. Remove old chunks if they exist
        removed_count = await self.remove_file_chunks(filename)
        if removed_count > 0:
            logger.info(f"  Removed {removed_count} old chunks")

        # 2. Read and parse file (run in thread pool to avoid blocking)
        file_path = storage_service._get_path(filename)
        parsed_doc = await asyncio.to_thread(
            document_parser_service.parse_file, file_path
        )

        # Check for parsing errors
        if parsed_doc.error:
            error_msg = f"Failed to parse {filename}: {parsed_doc.error}"
            logger.error(f"✗ {error_msg}")
            raise ValueError(error_msg)

        content = parsed_doc.content

        # 3. Split into chunks (CPU-bound, run in thread pool)
        chunks = await asyncio.to_thread(self.text_splitter.split_text, content)

        if not chunks:
            logger.warning(f"⚠ File is empty or too short: {filename}")
            raise ValueError(f"File is empty or too short: {filename}")

        logger.debug(f"  Split into {len(chunks)} chunks")

        # 4. Add chunks to vector store with metadata (I/O-bound, run in thread pool)
        metadatas = [
            {
                "source": filename,
                "chunk_id": i,
                "language": parsed_doc.language,
                **parsed_doc.metadata,
            }
            for i in range(len(chunks))
        ]

        await asyncio.to_thread(
            self.vector_store.add_texts, texts=chunks, metadatas=metadatas
        )

        logger.info(
            f"✓ Ingested {filename}: {len(chunks)} chunks added to vector store"
        )
        return {
            "status": "success",
            "filename": filename,
            "chunks_created": len(chunks),
        }

    async def ingest_all_files(self, max_concurrent: int = 3):
        """Ingest all files with controlled concurrency."""
        logger.info("[INGEST ALL] Starting bulk ingestion...")

        all_files = await asyncio.to_thread(storage_service.get_all_files)
        logger.info(f"  Found {len(all_files)} files in storage")

        if not all_files:
            logger.info("  No files to ingest")
            return {"status": "success", "files_processed": 0, "total_chunks": 0}

        semaphore = asyncio.Semaphore(max_concurrent)
        results = []
        errors = []

        async def ingest_with_limit(filename: str):
            async with semaphore:
                try:
                    result = await self.ingest_files(filename)
                    results.append(result)
                except Exception as e:
                    logger.error(f"✗ Failed to ingest {filename}: {e}")
                    errors.append({"filename": filename, "error": str(e)})

        await asyncio.gather(*[ingest_with_limit(f) for f in all_files])

        total_chunks = sum(r.get("chunks_created", 0) for r in results)
        logger.info(
            f"✓ Bulk ingestion complete: {len(results)} succeeded, {len(errors)} failed, {total_chunks} chunks"
        )

        return {
            "status": "success",
            "files_processed": len(results),
            "total_chunks": total_chunks,
            "errors": errors,
        }

    async def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Retrieve relevant chunks for a query (async, non-blocking).
        """
        logger.debug(f"[RETRIEVE] Query: '{query[:50]}...' (top_k={top_k})")

        results = await asyncio.to_thread(
            self.vector_store.similarity_search, query, k=top_k
        )

        chunks = [
            {"content": doc.page_content, "metadata": doc.metadata} for doc in results
        ]

        sources = set(chunk["metadata"].get("source", "unknown") for chunk in chunks)
        logger.debug(f"✓ Retrieved {len(chunks)} chunks from files: {sources}")

        return chunks

    async def remove_file_chunks(self, filename: str) -> int:
        """
        Remove all chunks for a given file (async, non-blocking).

        Returns:
            Number of chunks removed
        """
        logger.debug(f"[REMOVE] Checking for existing chunks: {filename}")

        try:
            existing = await asyncio.to_thread(
                self.vector_store.get, where={"source": filename}
            )

            if existing and existing.get("ids"):
                chunk_ids = existing["ids"]
                await asyncio.to_thread(self.vector_store.delete, ids=chunk_ids)
                logger.debug(f"✓ Removed {len(chunk_ids)} chunks for {filename}")
                return len(chunk_ids)

            logger.debug(f"  No existing chunks found for {filename}")
            return 0
        except Exception as e:
            logger.error(f"✗ Error removing chunks for {filename}: {e}")
            return 0
