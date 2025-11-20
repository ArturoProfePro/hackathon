from pathlib import Path
from fastapi import APIRouter, File, UploadFile
from fastapi.exceptions import HTTPException

from config import settings
from schemas.chat_prompt import PromptSchema, PromptResponseSchema
from services.chat_service import chat_service


router = APIRouter()


@router.post("/", response_model=PromptResponseSchema)
async def prompt(prompt: PromptSchema):
    """
    Обработчик POST запроса для чата.
    Принимает сообщение от пользователя и возвращает ответ от AI.
    Если указан corpus_id и RAG включен, использует RAG для генерации ответа.
    """
    return await chat_service.generate_response(
        prompt.message, corpus_id=prompt.corpus_id
    )
