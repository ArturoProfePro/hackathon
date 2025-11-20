from pathlib import Path
from fastapi import APIRouter, File, UploadFile
from fastapi.exceptions import HTTPException

import shutil

from config import settings
from services.rag_service import rag_service


router = APIRouter()


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    """
    Загружает файл на сервер.
    Если включен RAG, создаёт отдельный RAG‑корпус для этой книги
    и загружает файл в этот корпус, чтобы его можно было выбрать в чате.
    """
    if file.filename == "":
        raise HTTPException(status_code=400, detail="No file selected")

    # Сохраняем файл на диск
    file_path = settings.UPLOAD_DIR / file.filename
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Если RAG выключен — просто подтверждаем загрузку файла
    if not settings.RAG_ENABLED:
        return {
            "message": "Книга загружена, но RAG сейчас отключен. "
            "Включите RAG, чтобы использовать её в чате.",
            "location": str(file_path),
        }

    # Создаём отдельный корпус под эту книгу и загружаем в него файл
    try:
        # 1) создаём корпус c display_name = имени файла
        corpus = await rag_service.create_corpus(display_name=file.filename)

        # 2) загружаем файл в этот корпус
        rag_file_id = await rag_service.upload_file_to_corpus(
            corpus_id=corpus.name,
            file_path=str(file_path),
            display_name=file.filename,
        )

        return {
            "message": "Книга загружена и доступна для выбора в RAG‑чате.",
            "corpus_id": corpus.name,
            "corpus_name": corpus.display_name,
            "file_id": rag_file_id,
        }
    except Exception as e:
        # Не падаем, если RAG не сработал — файл все равно сохранён
        print(f"⚠️ Ошибка загрузки файла в RAG: {e}")
        return {
            "message": "Файл загружен, но не удалось добавить его в контекст RAG.",
            "location": str(file_path),
        }
