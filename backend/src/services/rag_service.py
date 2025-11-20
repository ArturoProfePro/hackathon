from functools import lru_cache
from typing import Optional, List, TYPE_CHECKING
from pathlib import Path

from schemas.rag import (
    CorpusSchema,
    CorpusCreateSchema,
    FileUploadSchema,
    QuerySchema,
    RAGResponseSchema,
    RelevantDocumentSchema,
)

if TYPE_CHECKING:
    from clients.gemini_rag_client import GeminiRagClient


class RagService:
    """
    Сервис для работы с RAG системой.
    Отвечает за бизнес-логику работы с корпусами документов и генерацией ответов.
    """

    def __init__(self, rag_client_instance: Optional["GeminiRagClient"] = None):
        """
        Инициализация RagService.

        Args:
            rag_client_instance: Экземпляр GeminiRagClient для работы с RAG API
        """
        self._rag_client_instance = rag_client_instance

    @property
    def rag_client(self) -> "GeminiRagClient":
        """
        Получает клиент RAG динамически.
        """
        if self._rag_client_instance is not None:
            return self._rag_client_instance
        # Импортируем динамически
        from clients.gemini_rag_client import gemini_rag_client
        if gemini_rag_client is None:
            raise RuntimeError("RAG клиент не инициализирован")
        return gemini_rag_client

    async def create_corpus(self, display_name: str) -> CorpusSchema:
        """
        Создает новый корпус для хранения документов.

        Args:
            display_name: Отображаемое имя корпуса

        Returns:
            CorpusSchema: Созданный корпус
        """
        corpus_id = self.rag_client.create_corpus(display_name)
        return CorpusSchema(
            name=corpus_id,
            display_name=display_name,
        )

    async def list_corpora(self) -> List[CorpusSchema]:
        """
        Получает список всех корпусов.

        Returns:
            List[CorpusSchema]: Список корпусов
        """
        corpora_data = self.rag_client.list_corpora()
        return [
            CorpusSchema(
                name=corpus["name"],
                display_name=corpus["display_name"],
                create_time=corpus.get("create_time"),
            )
            for corpus in corpora_data
        ]

    async def upload_file_to_corpus(
        self, corpus_id: str, file_path: str, display_name: Optional[str] = None
    ) -> str:
        """
        Загружает файл в корпус.

        Args:
            corpus_id: ID корпуса
            file_path: Путь к файлу
            display_name: Отображаемое имя файла

        Returns:
            str: ID загруженного файла
        """
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"Файл не найден: {file_path}")

        file_id = self.rag_client.upload_file_to_corpus(
            corpus_id=corpus_id,
            file_path=str(file_path_obj),
            display_name=display_name or file_path_obj.name,
        )
        return file_id

    async def query_corpus(
        self, corpus_id: str, query: str, max_results: int = 5
    ) -> List[RelevantDocumentSchema]:
        """
        Выполняет поиск релевантных документов в корпусе.

        Args:
            corpus_id: ID корпуса
            query: Поисковый запрос
            max_results: Максимальное количество результатов

        Returns:
            List[RelevantDocumentSchema]: Список релевантных документов
        """
        results = self.rag_client.query_corpus(
            corpus_id=corpus_id, query=query, max_results=max_results
        )
        return [
            RelevantDocumentSchema(
                file_uri=doc["file_uri"],
                chunk_uri=doc["chunk_uri"],
                chunk=doc["chunk"],
                relevance_score=doc.get("relevance_score"),
            )
            for doc in results
        ]

    async def generate_rag_response(
        self,
        corpus_id: str,
        query: str,
        model_name: str = "gemini-2.0-flash-exp",
        max_results: int = 5,
    ) -> RAGResponseSchema:
        """
        Генерирует ответ на основе релевантных документов из корпуса.

        Args:
            corpus_id: ID корпуса
            query: Запрос пользователя
            model_name: Название модели
            max_results: Максимальное количество релевантных документов

        Returns:
            RAGResponseSchema: Ответ с релевантными документами
        """
        # Получаем релевантные документы
        relevant_docs = await self.query_corpus(corpus_id, query, max_results)

        # Генерируем ответ
        response_text = self.rag_client.generate_rag_response(
            corpus_id=corpus_id,
            query=query,
            model_name=model_name,
            max_results=max_results,
        )

        return RAGResponseSchema(
            message=response_text,
            relevant_docs=[
                {
                    "file_uri": doc.file_uri,
                    "chunk_uri": doc.chunk_uri,
                    "chunk": doc.chunk,
                    "relevance_score": doc.relevance_score,
                }
                for doc in relevant_docs
            ],
        )


@lru_cache()
def get_rag_service() -> RagService:
    """
    Фабричная функция для создания экземпляра RagService.
    Использует lru_cache для singleton паттерна.
    """
    return RagService()


rag_service = get_rag_service()

