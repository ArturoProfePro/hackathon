from pydantic import BaseModel
from typing import Optional, List


class CorpusSchema(BaseModel):
    """Схема для корпуса документов."""
    name: str
    display_name: str
    create_time: Optional[str] = None


class CorpusCreateSchema(BaseModel):
    """Схема для создания корпуса."""
    display_name: str


class FileUploadSchema(BaseModel):
    """Схема для загрузки файла в корпус."""
    corpus_id: str
    file_path: str
    display_name: Optional[str] = None


class QuerySchema(BaseModel):
    """Схема для поискового запроса."""
    corpus_id: str
    query: str
    max_results: int = 5


class RAGResponseSchema(BaseModel):
    """Схема для RAG ответа."""
    message: str
    relevant_docs: Optional[List[dict]] = None


class RelevantDocumentSchema(BaseModel):
    """Схема для релевантного документа."""
    file_uri: str
    chunk_uri: str
    chunk: str
    relevance_score: Optional[float] = None

