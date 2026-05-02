from app.services.RAG import RAGService

# Initialize services
rag_service = RAGService()


async def initialize_rag():
    """Load all existing files into RAG on startup."""
    print("Ingesting existing files into RAG...")
    result = rag_service.ingest_all_files()
    print(
        f"Ingested {result['files_processed']} files, {result['total_chunks']} chunks"
    )
    return result
