from pathlib import Path
from fastapi import APIRouter, File, UploadFile
from fastapi.exceptions import HTTPException

from config import settings
from schemas.chat_prompt import PromptSchema
from services import chat_service


router = APIRouter()


@router.post("/")
async def prompt(prompt: PromptSchema):
    return prompt
