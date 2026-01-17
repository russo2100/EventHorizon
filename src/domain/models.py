from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

class EventBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    source: str = Field(..., description="Источник данных")
    content: str = Field(..., description="Текст события")
    timestamp: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class EventCreate(EventBase):
    pass

class Event(EventBase):
    id: str

class SearchQuery(BaseModel):
    query: str
    limit: int = Field(default=3, ge=1, le=10)
    min_score: float = 0.0
