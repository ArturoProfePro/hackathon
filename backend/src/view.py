from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse


router = APIRouter()

FRONTEND_INDEX = (Path(__file__).resolve().parents[2] / "dist" / "index.html").resolve()


@router.get("/")
async def index():
    if not FRONTEND_INDEX.exists():
        raise HTTPException(status_code=500, detail="Frontend bundle not found")
    return FileResponse(FRONTEND_INDEX)
