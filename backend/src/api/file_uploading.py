from pathlib import Path
from fastapi import APIRouter, File, UploadFile
from fastapi.exceptions import HTTPException

import shutil

from config import settings
from services.book_service import book_service


router = APIRouter()


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    if file.filename == "":
        raise HTTPException(status_code=400, detail="No file selected")

    return await book_service.upload_file(file)
