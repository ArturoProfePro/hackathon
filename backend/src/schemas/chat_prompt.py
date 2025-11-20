from pydantic import BaseModel
from typing import Optional


class PromptResponseSchema(BaseModel):
    message: str


class PromptSchema(BaseModel):
    message: str
    corpus_id: Optional[str] = None  # ID корпуса для RAG (опционально)
