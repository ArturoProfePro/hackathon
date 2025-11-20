from functools import lru_cache
from google import genai
from google.genai.errors import APIError

from config import settings


class GeminiClient:
    """
    Класс-обертка для взаимодействия с Gemini API.
    Инициализируется в FastAPI lifespan startup.
    """

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        """
        Инициализация клиента Gemini API.
        """
        self.model_name = model_name
        print(f"⚙️ Инициализация клиента Gemini API (модель: {self.model_name})...")

        try:
            self.client = genai.Client(api_key=api_key)
            print("🎉 Клиент Gemini API успешно инициализирован.")
        except Exception as e:
            raise RuntimeError(f"❌ Ошибка инициализации Gemini Client: {e}")

    def generate_text(self, prompt: str) -> str:
        """
        Отправляет одноразовый запрос на генерацию текста.
        """
        if self.client is None:
            return "❌ Ошибка: Клиент не инициализирован."

        print(f"⚙️ Запрос к модели {self.model_name}...")
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt],
            )
            return response.text
        except APIError as e:
            return f"❌ Ошибка API: {e}"
        except Exception as e:
            return f"❌ Непредвиденная ошибка: {e}"


# Глобальный экземпляр будет создан в lifespan
gemini_client: GeminiClient | None = None
