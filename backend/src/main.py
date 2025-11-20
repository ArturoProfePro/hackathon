from contextlib import asynccontextmanager
from typing import AsyncGenerator
from api import router as api_router
from config import settings
from services import chat_service
from view import router as view_router

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Инициализируем клиент Gemini при старте приложения
    from clients.gemini_client import GeminiClient
    import clients.gemini_client as gemini_module

    # Получаем model_name из settings, если есть, иначе используем значение по умолчанию
    model_name = getattr(settings, "model_name", "gemini-2.5-flash")
    gemini_client_instance = GeminiClient(
        api_key=settings.GEMINI_API_KEY, model_name=model_name
    )
    gemini_module.gemini_client = gemini_client_instance

    # Инициализируем RAG клиент, если RAG включен
    if settings.RAG_ENABLED:
        from clients.gemini_rag_client import GeminiRagClient
        import clients.gemini_rag_client as rag_module

        rag_module.gemini_rag_client = GeminiRagClient(
            genai_client=gemini_client_instance.client
        )
        print("✅ RAG клиент инициализирован.")

    yield


app = FastAPI(debug=True, lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешенный источник
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
app.include_router(view_router, prefix="")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
