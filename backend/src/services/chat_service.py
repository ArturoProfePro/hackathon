from functools import lru_cache
from typing import Optional, TYPE_CHECKING

from schemas.chat_prompt import PromptResponseSchema
from clients.gemini_client import gemini_client
from config import settings

if TYPE_CHECKING:
    from clients.gemini_client import GeminiClient
    from services.rag_service import RagService


class ChatService:
    """
    Сервис для обработки чат-запросов.
    Отвечает за бизнес-логику работы с чатом.
    """

    def __init__(
        self,
        gemini_client_instance: Optional["GeminiClient"] = None,
        rag_service_instance: Optional["RagService"] = None,
    ):
        """
        Инициализация ChatService.

        Args:
            gemini_client_instance: Экземпляр GeminiClient для генерации ответов
            rag_service_instance: Экземпляр RagService для RAG функциональности
        """
        self._gemini_client_instance = gemini_client_instance
        self._rag_service_instance = rag_service_instance

    @property
    def gemini_client(self):
        """
        Получает клиент Gemini динамически из модуля.
        Это позволяет использовать клиент, инициализированный в lifespan.
        """
        if self._gemini_client_instance is not None:
            return self._gemini_client_instance
        # Импортируем динамически, чтобы получить актуальное значение
        from clients.gemini_client import gemini_client
        return gemini_client

    @property
    def rag_service(self):
        """
        Получает RAG сервис динамически.
        """
        if self._rag_service_instance is not None:
            return self._rag_service_instance
        from services.rag_service import rag_service
        return rag_service

    async def generate_response(
        self, message: str, corpus_id: Optional[str] = None
    ) -> PromptResponseSchema:
        """
        Генерирует ответ на сообщение пользователя.
        Если указан corpus_id и RAG включен, использует RAG для генерации ответа.

        Args:
            message: Сообщение от пользователя
            corpus_id: ID корпуса для RAG (опционально)

        Returns:
            PromptResponseSchema: Ответ с сгенерированным текстом
        """
        # Используем RAG, если он включен и указан corpus_id
        use_rag = (
            settings.RAG_ENABLED
            and corpus_id is not None
            or (corpus_id is None and settings.RAG_ENABLED and settings.RAG_CORPUS_ID)
        )

        if use_rag:
            actual_corpus_id = corpus_id or settings.RAG_CORPUS_ID
            try:
                rag_response = await self.rag_service.generate_rag_response(
                    corpus_id=actual_corpus_id,
                    query=message,
                    model_name=settings.model_name,
                )
                return PromptResponseSchema(message=rag_response.message)
            except Exception as e:
                # Если RAG не сработал, fallback на обычную генерацию
                print(f"⚠️ Ошибка RAG, используем обычную генерацию: {e}")

        # Обычная генерация без RAG
        client = self.gemini_client
        if client is None:
            return PromptResponseSchema(
                message="❌ Ошибка: Клиент Gemini не инициализирован."
            )

        reply = client.generate_text(message)
        return PromptResponseSchema(message=reply)


@lru_cache()
def get_chat_service() -> ChatService:
    """
    Фабричная функция для создания экземпляра ChatService.
    Использует lru_cache для singleton паттерна.
    """
    return ChatService()


chat_service = get_chat_service()
