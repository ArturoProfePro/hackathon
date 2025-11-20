from functools import lru_cache
import shutil
from typing import Optional
from fastapi import UploadFile

from schemas.book import BookSchema
from config import settings


class BookService:
    async def upload_file(
        self, file: UploadFile, upload_to_rag: bool = False, corpus_id: Optional[str] = None
    ):
        """
        Загружает файл в хранилище и опционально в RAG корпус.

        Args:
            file: Загружаемый файл
            upload_to_rag: Загружать ли файл в RAG корпус
            corpus_id: ID корпуса для загрузки (если не указан, используется из настроек)

        Returns:
            BookSchema: Информация о загруженном файле
        """
        file_path = settings.UPLOAD_DIR / file.filename

        settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Загружаем в RAG, если требуется
        rag_file_id = None
        if upload_to_rag:
            try:
                from services.rag_service import rag_service

                actual_corpus_id = corpus_id or settings.RAG_CORPUS_ID
                if actual_corpus_id:
                    rag_file_id = await rag_service.upload_file_to_corpus(
                        corpus_id=actual_corpus_id,
                        file_path=str(file_path),
                        display_name=file.filename,
                    )
                    print(f"✅ Файл загружен в RAG корпус: {rag_file_id}")
            except Exception as e:
                print(f"⚠️ Ошибка загрузки файла в RAG: {e}")

        return BookSchema(
            filename=file.filename,
            content_type=file.content_type,
            size=file.size,
            location=str(file_path),
        )


@lru_cache()
def get_book_service():
    return BookService()


book_service = get_book_service()
