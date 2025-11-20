from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, File, UploadFile, Form
from fastapi.exceptions import HTTPException

import shutil

from config import settings
from services.rag_service import rag_service


router = APIRouter()


@router.post("/")
async def upload_files(
    files: List[UploadFile] = File(...),
    corpus_id: Optional[str] = Form(None),
):
    """
    Загружает один или несколько файлов.

    - Если `corpus_id` передан и RAG включен — файлы добавляются в существующий корпус.
    - Если corpus_id не передан, но RAG включен — создаётся новый корпус (по имени первого файла).
    - Если RAG выключен — файлы просто сохраняются на диск.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    saved_files = []
    for file in files:
        if file.filename == "":
            raise HTTPException(status_code=400, detail="One of files has empty name")

        file_path = settings.UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        saved_files.append({"filename": file.filename, "location": str(file_path)})

    if not settings.RAG_ENABLED:
        return {
            "message": "Файлы загружены, но RAG отключен. "
            "Включите RAG, чтобы использовать их в чате.",
            "files": saved_files,
        }

    # Если corpus_id не указан — создаём новый корпус по имени первого файла
    created_corpus = None
    target_corpus_id = corpus_id
    if target_corpus_id is None:
        corpus = await rag_service.create_corpus(display_name=files[0].filename)
        target_corpus_id = corpus.name
        created_corpus = corpus

    rag_results = []
    for info in saved_files:
        try:
            rag_file_id = await rag_service.upload_file_to_corpus(
                corpus_id=target_corpus_id,
                file_path=info["location"],
                display_name=info["filename"],
            )
            rag_results.append(
                {
                    "filename": info["filename"],
                    "file_id": rag_file_id,
                }
            )
        except Exception as e:
            print(f"⚠️ Ошибка загрузки файла {info['filename']} в RAG: {e}")

    return {
        "message": "Файлы загружены и доступны в RAG."
        if rag_results
        else "Файлы сохранены, но не удалось добавить их в RAG.",
        "corpus_id": target_corpus_id,
        "corpus_name": created_corpus.display_name
        if created_corpus
        else target_corpus_id,
        "uploaded": rag_results,
    }
