from typing import Optional, List
from pathlib import Path

from google import genai
from google.genai.errors import APIError
from docx import Document  # для извлечения текста из .docx
from pypdf import PdfReader  # для извлечения текста из .pdf

from config import settings


class GeminiRagClient:
    """
    Упрощённый RAG‑клиент поверх локальных файлов.
    Вместо официального Gemini RAG API (corpora, files и т.п.)
    мы используем обычный Gemini client и локальные файлы как «корпуса».

    Корпус = директория в `UPLOAD_DIR / \"corpora\" / <corpus_id>`,
    где лежат файлы книги.
    """

    def __init__(self, genai_client: genai.Client):
        """
        Инициализация клиента RAG.

        Args:
            genai_client: Экземпляр genai.Client для работы с API
        """
        self.client = genai_client
        self.corpora_root = settings.UPLOAD_DIR / "corpora"
        self.corpora_root.mkdir(parents=True, exist_ok=True)

    def _corpus_dir(self, corpus_id: str) -> Path:
        return self.corpora_root / corpus_id

    def create_corpus(self, display_name: str) -> str:
        """
        Создаёт «корпус» как локальную директорию.

        Возвращает corpus_id, который равен имени директории.
        """
        # corpus_id можно сделать просто из имени файла + суффикс
        safe_name = display_name.replace("/", "_").replace("\\", "_")
        corpus_dir = self._corpus_dir(safe_name)
        corpus_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Локальный корпус '{display_name}' создан: {corpus_dir}")
        return safe_name

    def list_corpora(self) -> List[dict]:
        """
        Возвращает список локальных корпусов (директорий).
        """
        corpora: List[dict] = []
        if not self.corpora_root.exists():
            return corpora

        for d in self.corpora_root.iterdir():
            if d.is_dir():
                corpora.append(
                    {
                        "name": d.name,
                        "display_name": d.name,
                        "create_time": None,
                    }
                )
        return corpora

    def list_files(self, corpus_id: str) -> List[dict]:
        """
        Возвращает список файлов в указанном корпусе.
        """
        corpus_dir = self._corpus_dir(corpus_id)
        if not corpus_dir.exists():
            raise FileNotFoundError(f"Корпус не найден: {corpus_id}")

        files: List[dict] = []
        for f in corpus_dir.iterdir():
            if f.is_file():
                files.append(
                    {
                        "corpus_id": corpus_id,
                        "filename": f.name,
                        "size": f.stat().st_size,
                    }
                )
        return files

    def upload_file_to_corpus(
        self, corpus_id: str, file_path: str, display_name: Optional[str] = None
    ) -> str:
        """
        Копирует файл в директорию корпуса.
        """
        src = Path(file_path)
        if not src.exists():
            raise FileNotFoundError(f"Файл не найден: {file_path}")

        corpus_dir = self._corpus_dir(corpus_id)
        corpus_dir.mkdir(parents=True, exist_ok=True)

        target_name = display_name or src.name
        dst = corpus_dir / target_name
        dst.write_bytes(src.read_bytes())

        print(f"✅ Файл {src} добавлен в локальный корпус {corpus_id} как {dst.name}")
        return str(dst)

    def delete_file(self, corpus_id: str, filename: str) -> bool:
        """
        Удаляет файл из корпуса.
        """
        corpus_dir = self._corpus_dir(corpus_id)
        f = corpus_dir / filename
        if not f.exists():
            return False
        f.unlink()
        print(f"🗑️ Файл {f} удалён из корпуса {corpus_id}")
        return True

    def delete_corpus(self, corpus_id: str) -> bool:
        """
        Удаляет корпус и все файлы внутри.
        """
        corpus_dir = self._corpus_dir(corpus_id)
        if not corpus_dir.exists():
            return False

        # Удаляем все файлы
        for f in corpus_dir.iterdir():
            if f.is_file():
                f.unlink()
        # И саму директорию
        corpus_dir.rmdir()
        print(f"🗑️ Корпус {corpus_id} удалён")
        return True

    def _read_corpus_text(self, corpus_id: str) -> str:
        """
        Читает содержимое всех файлов в корпусе и склеивает в один текст.

        - Для .txt / .md читаем как обычный текст
        - Для .docx используем python-docx
        - Для бинарных файлов (pdf, png и т.п.) пытаемся прочитать как текст,
          но если там в основном бинарные данные — пропускаем
        """
        corpus_dir = self._corpus_dir(corpus_id)
        if not corpus_dir.exists():
            raise FileNotFoundError(f"Корпус не найден: {corpus_id}")

        parts: List[str] = []

        for f in corpus_dir.iterdir():
            if not f.is_file():
                continue

            suffix = f.suffix.lower()

            # Текстовые файлы
            if suffix in {".txt", ".md", ".markdown"}:
                try:
                    text = f.read_text(encoding="utf-8", errors="ignore")
                    if text.strip():
                        parts.append(f"Файл {f.name}:\n{text}")
                except Exception:
                    continue
                continue

            # DOCX-файлы (книги / документы Word)
            if suffix == ".docx":
                try:
                    doc = Document(str(f))
                    text = "\n".join(p.text for p in doc.paragraphs)
                    if text.strip():
                        parts.append(f"Файл {f.name}:\n{text}")
                except Exception:
                    # Если не удалось распарсить, просто пропускаем
                    continue
                continue

            # PDF-файлы
            if suffix == ".pdf":
                try:
                    reader = PdfReader(str(f))
                    pages_text: List[str] = []
                    for page in reader.pages:
                        try:
                            page_text = page.extract_text() or ""
                        except Exception:
                            page_text = ""
                        if page_text.strip():
                            pages_text.append(page_text)
                    text = "\n\n".join(pages_text)
                    if text.strip():
                        parts.append(f"Файл {f.name}:\n{text}")
                except Exception:
                    # Если не удалось распарсить PDF, пропускаем
                    continue
                continue

            # Всё остальное пытаемся прочитать как текст,
            # но фильтруем очевидный бинарник
            try:
                raw = f.read_bytes()
                # Простая эвристика: доля непечатных символов
                sample = raw[:2000]
                non_printable = sum(1 for b in sample if b < 9 or (13 < b < 32))
                if sample and non_printable / len(sample) > 0.3:
                    # Похоже на бинарный файл — пропускаем
                    continue
                text = sample.decode("utf-8", errors="ignore")
                if text.strip():
                    parts.append(f"Файл {f.name} (часть содержимого):\n{text}")
            except Exception:
                continue

        return "\n\n".join(parts)

    def query_corpus(
        self, corpus_id: str, query: str, max_results: int = 5
    ) -> List[dict]:
        """
        Упрощённый «поиск»: возвращаем один большой чанк со всем текстом корпуса.
        """
        text = self._read_corpus_text(corpus_id)
        if not text:
            return []

        return [
            {
                "file_uri": corpus_id,
                "chunk_uri": f"{corpus_id}#0",
                "chunk": text,
                "relevance_score": 1.0,
            }
        ]

    def generate_rag_response(
        self,
        corpus_id: str,
        query: str,
        model_name: str = "gemini-2.5-flash",
        max_results: int = 5,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Генерирует ответ на основе текста из выбранного «корпуса» (книги).
        """
        try:
            relevant_docs = self.query_corpus(corpus_id, query, max_results)

            if not relevant_docs:
                return (
                    "Извините, не удалось прочитать загруженную книгу "
                    "или в ней нет текста."
                )

            context = "\n\n".join(
                [
                    f"Документ {i+1}:\n{doc['chunk']}"
                    for i, doc in enumerate(relevant_docs)
                ]
            )

            base_prompt = system_prompt or (
                "Ты ассистент, который отвечает на вопросы по книге. "
                "Отвечай просто, без форматирования."
            )

            prompt = f"""{base_prompt}

Контекст (текст книги или её части):
{context}

Вопрос пользователя: {query}

Дай развёрнутый ответ, опираясь ТОЛЬКО на текст выше. Если ответа нет в тексте, честно скажи об этом.
Ответ:"""

            response = self.client.models.generate_content(
                model=model_name,
                contents=[prompt],
            )

            return response.text
        except APIError as e:
            return f"❌ Ошибка генерации RAG ответа: {e}"
        except Exception as e:
            return f"❌ Непредвиденная ошибка при генерации ответа: {e}"


# Глобальный экземпляр будет создан в lifespan
gemini_rag_client: GeminiRagClient | None = None

