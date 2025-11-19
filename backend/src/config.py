from functools import lru_cache
from pathlib import Path
from pydantic.v1.typing import StrPath
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    UPLOAD_DIR: Path = Path("uploads")
    GEMINI_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env.example",
        case_sensitive=False,
    )


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()

print(settings.GEMINI_API_KEY)
