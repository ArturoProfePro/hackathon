from functools import lru_cache
import shutil
from fastapi import UploadFile

from schemas.book import BookSchema
from config import settings


class BookService:
    async def upload_file(self, file: UploadFile):
        file_path = settings.UPLOAD_DIR / file.filename

        settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

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
