from .file_uploading import router as upload_router
from .chat import router as chat_router
from .rag import router as rag_router
from fastapi import APIRouter

router = APIRouter()

router.include_router(upload_router, prefix="/upload_file")
router.include_router(chat_router, prefix="/chat")
router.include_router(rag_router, prefix="/rag")
