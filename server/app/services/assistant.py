"""
AI Assistant service using LLM with RAG context.
Answers user questions based on retrieved document chunks.
"""

from langchain_openai import ChatOpenAI

from app.core.logger import logger
from app.core.settings import settings
from app.core.startup import rag_service


class AssistantService:
    """
    Service for answering questions using LLM + RAG.

    Architecture:
    1. User asks question
    2. RAG retrieves relevant chunks from vector store
    3. Chunks are formatted as context
    4. LLM generates answer based on context
    """

    def __init__(self):
        logger.info("Initializing Assistant service...")

        self.llm = ChatOpenAI(
            api_key=settings.groq_api_key,
            base_url="https://openrouter.ai/api/v1",
            model="meta-llama/llama-3.1-8b-instruct",
        )
        logger.debug("✓ LLM client configured (llama-3.1-8b via OpenRouter)")

        self.rag_service = rag_service
        logger.info("✓ Assistant service ready")

    async def answer_question(self, question: str) -> str:
        logger.info(f"[ASSISTANT] Question: '{question[:100]}...'")

        # Step 1: Retrieve relevant chunks
        relevant_chunks = self.rag_service.retrieve(question, top_k=5)

        # Step 2: Build context
        if not relevant_chunks:
            context = "База знаний пуста."
            logger.warning("⚠ No chunks retrieved - knowledge base is empty")
        else:
            context_parts = [
                f"--- DOCUMENT: {chunk['metadata']['source']} ---\n{chunk['content']}"
                for chunk in relevant_chunks
            ]
            context = "\n\n".join(context_parts)

            sources = set(chunk["metadata"]["source"] for chunk in relevant_chunks)
            logger.info(f"  Retrieved {len(relevant_chunks)} chunks from: {sources}")

        # Step 3: Build system prompt
        system_prompt = (
            "You are the Lead Engineering Assistant for the AI Knowledge Hub. "
            "Your role is to analyze the provided technical documentation and source files to deliver precise, context-aware answers. "
            "\n\nOPERATING GUIDELINES:\n"
            "1. Use ONLY the provided CONTEXT to answer the query. If the information is missing, state that you do not have enough data.\n"
            "2. Be concise, professional, and technical. Use Markdown for code snippets and bold text for key terms.\n"
            "3. When referring to specific files or modules, always use their exact names as found in the context.\n"
            "4. If the user asks for code, ensure it follows the architecture described in the hub.\n"
            f"\n\nCONTEXT:\n{context}"
        )

        try:
            # Step 4: Send to LLM
            logger.debug("  Sending request to LLM...")
            response = await self.llm.ainvoke(
                [("system", system_prompt), ("human", question)]
            )

            # Extract text from response
            if response is None:
                logger.error("✗ LLM returned None")
                return "Ошибка: пустой ответ от модели"

            if isinstance(response, str):
                answer = response
            elif hasattr(response, "content"):
                answer = response.content
            else:
                answer = str(response)

            logger.info(f"✓ Answer generated ({len(answer)} chars)")
            return answer

        except Exception as e:
            logger.error(f"✗ LLM error: {type(e).__name__}: {e}")
            return f"Ошибка ответа от llama: {str(e)}"


assistant_service = AssistantService()
