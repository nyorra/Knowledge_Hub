from langchain_openai import ChatOpenAI

from app.core.settings import settings
from app.core.startup import rag_service


class AssistantService:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.groq_api_key,
            base_url="https://openrouter.ai/api/v1",
            model="meta-llama/llama-3.1-8b-instruct",
        )
        self.rag_service = rag_service

    async def answer_question(self, question: str) -> str:
        relevant_chunks = self.rag_service.retrieve(question, top_k=5)

        if not relevant_chunks:
            context = "База знаний пуста."
        else:
            context_parts = [
                f"--- DOCUMENT: {chunk['metadata']['source']} ---\n{chunk['content']}"
                for chunk in relevant_chunks
            ]
            context = "\n\n".join(context_parts)

        system_prompt = (
            "Ты — инженерный ассистент системы AI Knowledge Hub. "
            "Используй предоставленный ниже контекст для ответа на вопросы. "
            "Если в контексте нет ответа, так и скажи."
            f"\n\nКОНТЕКСТ:\n{context}"
        )

        try:
            response = await self.llm.ainvoke(
                [("system", system_prompt), ("human", question)]
            )

            if response is None:
                return "Ошибка: пустой ответ от модели"

            if isinstance(response, str):
                return response

            if hasattr(response, "content"):
                return response.content

            return str(response)

        except Exception as e:
            print(f"[AI ERROR] {type(e)}: {e}")
            return f"Ошибка ответа от llama: {str(e)}"


assistant_service = AssistantService()
