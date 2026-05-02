"""
Retrieval-Augmented Generation (RAG) service.
Manages vector embeddings and semantic search for knowledge retrieval.

Architecture:
- Embeddings: sentence-transformers/all-MiniLM-L6-v2 (local, CPU)
- Vector Store: ChromaDB (persistent)
- Chunking: RecursiveCharacterTextSplitter (1000 chars, 200 overlap)
"""

from pathlib import Path

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.logger import logger
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

    def ingest_files(self, filename: str):
        logger.info(f"[INGEST] Processing file: {filename}")

        # 1. Remove old chunks if they exist
        removed_count = self.remove_file_chunks(filename)
        if removed_count > 0:
            logger.info(f"  Removed {removed_count} old chunks")

        # 2. Read file content
        content = storage_service.get_file_content(filename)
        if content is None:
            logger.error(f"✗ File not found in storage: {filename}")
            return {"status": "error", "message": f"File {filename} not found"}

        # 3. Split into chunks
        chunks = self.text_splitter.split_text(content)

        if not chunks:
            logger.warning(f"⚠ File is empty or too short: {filename}")
            return {"status": "warning", "message": "File is empty or too short"}

        logger.debug(f"  Split into {len(chunks)} chunks")

        # 4. Add chunks to vector store with metadata
        self.vector_store.add_texts(
            texts=chunks,
            metadatas=[{"source": filename, "chunk_id": i} for i in range(len(chunks))],
        )

        logger.info(
            f"✓ Ingested {filename}: {len(chunks)} chunks added to vector store"
        )
        return {
            "status": "success",
            "filename": filename,
            "chunks_created": len(chunks),
        }

    def ingest_all_files(self):
        logger.info("[INGEST ALL] Starting bulk ingestion...")

        all_files = storage_service.get_all_files()
        logger.info(f"  Found {len(all_files)} files in storage")

        results = []
        for filename in all_files:
            result = self.ingest_files(filename)
            results.append(result)

        total_chunks = sum(r.get("chunks_created", 0) for r in results)
        logger.info(
            f"✓ Bulk ingestion complete: {len(results)} files, {total_chunks} chunks"
        )

        return {
            "status": "success",
            "files_processed": len(results),
            "total_chunks": total_chunks,
        }

    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        logger.debug(f"[RETRIEVE] Query: '{query[:50]}...' (top_k={top_k})")

        results = self.vector_store.similarity_search(query, k=top_k)

        chunks = [
            {"content": doc.page_content, "metadata": doc.metadata} for doc in results
        ]

        sources = set(chunk["metadata"].get("source", "unknown") for chunk in chunks)
        logger.debug(f"✓ Retrieved {len(chunks)} chunks from files: {sources}")

        return chunks

    def remove_file_chunks(self, filename: str):
        logger.debug(f"[REMOVE] Checking for existing chunks: {filename}")

        try:
            existing = self.vector_store.get(where={"source": filename})

            if existing and existing.get("ids"):
                chunk_ids = existing["ids"]
                self.vector_store.delete(ids=chunk_ids)
                logger.debug(f"✓ Removed {len(chunk_ids)} chunks for {filename}")
                return len(chunk_ids)

            logger.debug(f"  No existing chunks found for {filename}")
            return 0
        except Exception as e:
            logger.error(f"✗ Error removing chunks for {filename}: {e}")
            return 0
