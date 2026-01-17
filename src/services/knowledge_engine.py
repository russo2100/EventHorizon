# src/services/knowledge_engine.py
import uuid
import os
from txtai.embeddings import Embeddings
from loguru import logger
from src.core.config import settings
from src.domain.models import Event, EventCreate

class KnowledgeEngine:
    def __init__(self):
        self.embeddings = Embeddings({
            "path": "sentence-transformers/all-MiniLM-L6-v2",
            "content": True,
            "autodbm": True
        })
        self._load_or_create()

    def _load_or_create(self):
        # Проверяем наличие файла внутри относительной папки
        if os.path.exists(f"{settings.INDEX_PATH_STR}/embeddings"):
            try:
                self.embeddings.load(settings.INDEX_PATH_STR)
                logger.info(f"Индекс загружен из: {settings.INDEX_PATH_STR}")
            except Exception as e:
                logger.error(f"Ошибка загрузки (возможно поврежден): {e}")
        else:
            logger.info("Индекс будет создан с нуля.")

    def add_event(self, event_in: EventCreate) -> Event:
        event_id = str(uuid.uuid4())
        event = Event(id=event_id, **event_in.model_dump())
        
        # Добавляем в память
        self.embeddings.upsert([(event_id, event.content, None)])
        
        # Сохраняем по ОТНОСИТЕЛЬНОМУ пути
        try:
            self.embeddings.save(settings.INDEX_PATH_STR)
            logger.success(f"Событие {event_id} сохранено.")
        except Exception as e:
            logger.error(f"Ошибка FAISS при записи в '{settings.INDEX_PATH_STR}': {e}")
            # Дополнительный лог для понимания, где мы находимся
            logger.error(f"Текущая директория: {os.getcwd()}")
            raise e
            
        return event
    
    def search(self, query: str, limit: int = 3):
        try:
            logger.info(f"Выполняется поиск по запросу: {query}")
            
            # Выполняем поиск
            # txtai возвращает список словарей, если content=True, 
            # или список кортежей (id, score), если нет.
            raw_results = self.embeddings.search(query, limit)
            
            normalized_results = []
            for res in raw_results:
                # Нормализуем результат к единому виду
                if isinstance(res, dict):
                    normalized_results.append({
                        "id": res.get("id"),
                        "text": res.get("text"),
                        "score": round(float(res.get("score", 0)), 4)
                    })
                elif isinstance(res, tuple):
                    normalized_results.append({
                        "id": res[0],
                        "score": round(float(res[1]), 4)
                    })
            
            logger.info(f"Найдено результатов: {len(normalized_results)}")
            return normalized_results
            
        except Exception as e:
            logger.error(f"Ошибка при выполнении поиска: {e}")
            # Возвращаем пустой список, чтобы API не падало с 500 ошибкой
            return []



engine = KnowledgeEngine()
