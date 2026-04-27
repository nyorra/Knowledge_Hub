from langchain_openai import ChatOpenAI

from app.services.storage import storage_service
from app.Settings import settings


class AssistantService:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.groq_api_key,
            base_url="https://openrouter.ai/api/v1",
            model="meta-llama/llama-3.1-8b-instruct",
        )

    def _get_all_file_context(self) -> str:
        """Внутренний метод для агрегации текстов из всех файлов."""
        filenames = storage_service.get_all_files()
        context_parts = []

        for name in filenames:
            content = storage_service.get_file_content(name)
            if content:
                context_parts.append(f"--- DOCUMENT: {name} ---\n{content}")

        return "\n\n".join(context_parts) if context_parts else "База знаний пуста."

    async def answer_question(self, question: str) -> str:
        context = self._get_all_file_context()

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
