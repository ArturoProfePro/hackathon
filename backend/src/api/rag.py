from fastapi import APIRouter, HTTPException
from typing import Optional

from schemas.rag import (
    CorpusSchema,
    CorpusCreateSchema,
    QuerySchema,
    RAGResponseSchema,
)
from services.rag_service import rag_service
from config import settings


router = APIRouter()


@router.post("/corpus", response_model=CorpusSchema)
async def create_corpus(corpus: CorpusCreateSchema):
    """
    Создает новый корпус для хранения документов.
    """
    if not settings.RAG_ENABLED:
        raise HTTPException(
            status_code=400, detail="RAG не включен. Установите RAG_ENABLED=true"
        )

    return await rag_service.create_corpus(corpus.display_name)


@router.get("/corpus", response_model=list[CorpusSchema])
async def list_corpora():
    """
    Получает список всех корпусов.
    """
    if not settings.RAG_ENABLED:
        raise HTTPException(
            status_code=400, detail="RAG не включен. Установите RAG_ENABLED=true"
        )

    return await rag_service.list_corpora()


@router.post("/query", response_model=RAGResponseSchema)
async def query_corpus(query: QuerySchema):
    """
    Выполняет поиск в корпусе и генерирует ответ на основе найденных документов.
    """
    if not settings.RAG_ENABLED:
        raise HTTPException(
            status_code=400, detail="RAG не включен. Установите RAG_ENABLED=true"
        )

    return await rag_service.generate_rag_response(
        corpus_id=query.corpus_id,
        query=query.query,
        max_results=query.max_results,
    )

