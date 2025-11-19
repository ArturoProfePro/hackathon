import os
from google import genai
from google.genai.errors import APIError


class GeminiClient:
    """
    Класс-обертка для взаимодействия с Gemini API.
    Инициализация выделена в отдельный метод.
    """

    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.client: genai.Client | None = None
        self.model_name = model_name
        print(
            f"✅ GeminiClient создан. Модель: {self.model_name}. Ожидание инициализации..."
        )

    def init_client(self, api_key: str):
        """
        Метод инициализации, вызываемый в FastAPI lifespan startup.
        """
        print("⚙️ Инициализация клиента Gemini API...")
        if api_key == "":
            raise EnvironmentError(
                "Переменная окружения 'GEMINI_API_KEY' не найдена. "
                "Установите свой ключ API."
            )

        try:
            self.client = genai.Client()
            print("🎉 Клиент Gemini API успешно инициализирован.")
        except Exception as e:
            raise RuntimeError(f"❌ Ошибка инициализации Gemini Client: {e}")

    def generate_text(self, prompt: str) -> str:
        """
        Отправляет одноразовый запрос на генерацию текста (должен быть вызван после init_client).
        """
        if self.client is None:
            return (
                "❌ Ошибка: Клиент не инициализирован. Вызовите init_client() первым."
            )

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


def get_gemini_client():
    return GeminiClient()


gemini_client = get_gemini_client()
