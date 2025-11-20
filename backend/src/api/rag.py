from fastapi import APIRouter, HTTPException
from typing import Optional

from schemas.rag import (
    CorpusSchema,
    CorpusCreateSchema,
    QuerySchema,
    RAGResponseSchema,
    FileInfoSchema,
)
from services.rag_service import rag_service
from config import settings


router = APIRouter()


def _ensure_rag_enabled():
    if not settings.RAG_ENABLED:
        raise HTTPException(
            status_code=400, detail="RAG не включен. Установите RAG_ENABLED=true"
        )


@router.post("/corpus", response_model=CorpusSchema)
async def create_corpus(corpus: CorpusCreateSchema):
    """
    Создает новый корпус для хранения документов.
    """
    _ensure_rag_enabled()
    return await rag_service.create_corpus(corpus.display_name)


@router.get("/corpus", response_model=list[CorpusSchema])
async def list_corpora():
    """
    Получает список всех корпусов.
    """
    _ensure_rag_enabled()
    return await rag_service.list_corpora()


@router.delete("/corpus/{corpus_id}")
async def delete_corpus(corpus_id: str):
    """
    Удаляет корпус и все его файлы.
    """
    _ensure_rag_enabled()
    deleted = await rag_service.delete_corpus(corpus_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Корпус не найден")
    return {"status": "ok"}


@router.get("/corpus/{corpus_id}/files", response_model=list[FileInfoSchema])
async def list_files(corpus_id: str):
    """
    Получает список файлов в корпусе (книги).
    """
    _ensure_rag_enabled()
    return await rag_service.list_files(corpus_id)


@router.delete("/corpus/{corpus_id}/files/{filename}")
async def delete_file(corpus_id: str, filename: str):
    """
    Удаляет конкретный файл из корпуса.
    """
    _ensure_rag_enabled()
    deleted = await rag_service.delete_file(corpus_id, filename)
    if not deleted:
        raise HTTPException(status_code=404, detail="Файл не найден")
    return {"status": "ok"}


@router.post("/query", response_model=RAGResponseSchema)
async def query_corpus(query: QuerySchema):
    """
    Выполняет поиск в корпусе и генерирует ответ на основе найденных документов.
    """
    _ensure_rag_enabled()
    return await rag_service.generate_rag_response(
        corpus_id=query.corpus_id,
        query=query.query,
        max_results=query.max_results,
    )
