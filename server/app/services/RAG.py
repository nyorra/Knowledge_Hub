# A Retrieval-Augmented Generation (RAG) - Генерация с улучшенным извлечением информации
from pathlib import Path

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.services.storage import storage_service


class RAGService:
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize RAG service with embeddings model and vector store.

        Args:
            persist_directory: Where ChromaDB stores its data
        """
        # 1. Initialize text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""],
        )

        # 2. Initialize embedding model
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
        )

        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(exist_ok=True)

        # 3. Initialize ChromaDB vector store
        self.vector_store = Chroma(
            collection_name="knowledge_hub",
            embedding_function=self.embeddings,
            persist_directory=str(self.persist_directory),
        )

    def ingest_files(self, filename: str):
        """
        Ingest a file into vector store.
        Always removes old chunks first to prevent duplicates.
        """
        # 1. Remove old chunks if they exist
        removed_count = self.remove_file_chunks(filename)
        if removed_count > 0:
            print(f"[RAG] Removed {removed_count} old chunks for {filename}")

        # 2. Read file content
        content = storage_service.get_file_content(filename)
        if content is None:
            return {"status": "error", "message": f"File {filename} not found"}

        # 3. Split into chunks
        chunks = self.text_splitter.split_text(content)

        if not chunks:
            return {"status": "warning", "message": "File is empty or too short"}

        # 4. Add fresh chunks
        self.vector_store.add_texts(
            texts=chunks,
            metadatas=[{"source": filename, "chunk_id": i} for i in range(len(chunks))],
        )

        return {
            "status": "success",
            "filename": filename,
            "chunks_created": len(chunks),
        }

    def ingest_all_files(self):
        """
        Load all files from storage into vector DB.
        Call this once when initializing or when files are uploaded.
        """
        all_files = storage_service.get_all_files()

        results = []
        for filename in all_files:
            result = self.ingest_files(filename)
            results.append(result)

        return {
            "status": "success",
            "files_processed": len(results),
            "total_chunks": sum(r.get("chunks_created", 0) for r in results),
        }

    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Find most relevant chunks for a query.

        Args:
            query: User's question
            top_k: Number of chunks to return

        Returns:
            List of dicts with 'content' and 'metadata'
        """
        results = self.vector_store.similarity_search(query, k=top_k)

        return [
            {"content": doc.page_content, "metadata": doc.metadata} for doc in results
        ]

    def remove_file_chunks(self, filename: str):
        """Remove all chunks for a specific file before re-ingesting."""
        try:
            # ChromaDB's get() with where filter
            existing = self.vector_store.get(where={"source": filename})

            if existing and existing.get("ids"):
                self.vector_store.delete(ids=existing["ids"])
                return len(existing["ids"])
            return 0
        except Exception as e:
            print(f"[RAG] Error removing chunks for {filename}: {e}")
            return 0
