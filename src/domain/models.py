from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any

class Event(BaseModel):
    """Базовая модель события"""
    id: Optional[int] = Field(None, description="ID события в базе")
    content: str = Field(..., description="Текстовое содержание события")
    metadata: Optional[dict] = Field(default_factory=dict, description="Дополнительные данные")

class SearchQuery(BaseModel):
    """Модель поискового запроса"""
    query: str = Field(..., description="Текст запроса")
    limit: int = Field(default=5, ge=1, le=20)

class SearchResult(BaseModel):
    """Индивидуальный результат поиска"""
    id: Any = Field(..., description="ID найденного события")
    text: str = Field(..., description="Текст события")
    score: float = Field(..., description="Оценка релевантности (0-1)")

class AnalysisResponse(BaseModel):
    """Модель ответа аналитического модуля (RAG/KAG)"""
    query: str = Field(..., description="Исходный запрос пользователя")
    analysis: str = Field(..., description="Сгенерированный LLM анализ")
    relevant_events: List[SearchResult] = Field(..., description="События, на которых основан ответ")
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "Анализ рисков по газу",
                "analysis": "LLM вывод на основе найденных данных...",
                "relevant_events": []
            }
        }
    )
