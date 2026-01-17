import os
from typing import Any, Dict, List, Optional, Tuple, Union

from loguru import logger

from src.core.config import settings
from src.domain.models import SearchResult

try:
    # txtai опционален: если его нет, сервис должен стартовать без падения
    from txtai import Embeddings  # type: ignore
except ModuleNotFoundError:
    Embeddings = None  # type: ignore


class KnowledgeEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return

        self.index_path: str = settings.INDEX_PATH
        self.embeddings = self._create_embeddings()
        self.documents: List[Dict[str, Any]] = []

        self._load_index()
        self._initialized = True

    def _create_embeddings(self):
        if Embeddings is None:
            logger.warning("txtai is not installed: KnowledgeEngine работает в режиме заглушки (без поиска).")
            return None
        try:
            return Embeddings()
        except Exception as e:
            logger.exception(f"Не удалось создать Embeddings(): {e}")
            return None

    def _ensure_enabled(self) -> bool:
        if self.embeddings is None:
            return False
        return True

    def _load_index(self) -> None:
        """Загрузка существующего индекса, если он есть на диске."""
        if not self._ensure_enabled():
            return

        if os.path.exists(self.index_path):
            try:
                self.embeddings.load(self.index_path)
                logger.info(f"Индекс загружен из {self.index_path}")
            except Exception as e:
                logger.warning(f"Не удалось загрузить индекс: {e}")
                # пересоздаём embeddings, чтобы не жить в поломанном состоянии
                self.embeddings = self._create_embeddings()

    def add_event(self, content: str, metadata: Dict[str, Any]) -> int:
        """Добавление события в индекс (и in-memory список документов)."""
        event_id = len(self.documents)

        self.documents.append(
            {
                "id": event_id,
                "text": content,
                "metadata": metadata,
            }
        )

        # Если txtai отключён — просто возвращаем id, без индексации
        if not self._ensure_enabled():
            logger.warning("add_event: txtai недоступен, событие сохранено только в памяти (без индекса).")
            return event_id

        try:
            # txtai индексирует список (id, text, tags/metadata/None)
            self.embeddings.index([(doc["id"], doc["text"], None) for doc in self.documents])

            # Сохранение на диск
            os.makedirs(os.path.dirname(self.index_path) or ".", exist_ok=True)
            self.embeddings.save(self.index_path)
        except Exception as e:
            logger.exception(f"Ошибка индексации/сохранения: {e}")

        return event_id

    def search(self, query: str, limit: int = 5) -> List[SearchResult]:
        """Семантический поиск по документам."""
        if not self.documents:
            logger.warning("База событий пуста")
            return []

        if not self._ensure_enabled():
            logger.warning("search: txtai недоступен, возвращаю пустой список.")
            return []

        try:
            results = self.embeddings.search(query, limit)
        except Exception as e:
            logger.exception(f"Ошибка поиска: {e}")
            return []

        if not results:
            return []

        search_results: List[SearchResult] = []

        for doc_id, score in self._normalize_results(results):
            doc = next((d for d in self.documents if d["id"] == doc_id), None)
            if not doc:
                continue

            search_results.append(
                SearchResult(
                    id=doc_id,
                    text=doc["text"],
                    score=float(score),
                )
            )

        return search_results

    def _normalize_results(
        self, results: Any
    ) -> List[Tuple[int, float]]:
        """
        txtai может вернуть:
        - list[tuple(id, score)]
        - list[dict] с ключами id/score
        Нормализуем к list[(id:int, score:float)].
        """
        normalized: List[Tuple[int, float]] = []

        if not isinstance(results, list):
            return normalized

        for item in results:
            doc_id: Optional[int] = None
            score: float = 0.0

            if isinstance(item, tuple) and len(item) >= 2:
                doc_id = int(item[0])
                score = float(item[1])
            elif isinstance(item, dict):
                if "id" in item:
                    doc_id = int(item.get("id"))
                score = float(item.get("score", 0.0))
            else:
                continue

            if doc_id is None:
                continue

            normalized.append((doc_id, score))

        return normalized


# Singleton instance (как у тебя было)
knowledge_engine = KnowledgeEngine()
