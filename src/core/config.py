from pydantic_settings import BaseSettings
from typing import Optional  # ← ДОБАВИЛИ ЭТУ СТРОКУ

class Settings(BaseSettings):
    PROJECT_NAME: str = "EventHorizon"
    INDEX_PATH: str = "data/txtai_index"
    OPENROUTER_API_KEY: Optional[str] = None  # Теперь Optional определен
    LLM_MODEL: str = "tngtech/deepseek-r1t2-chimera:free"  # Обновили модель
    
    model_config = {
        "env_file": ".env",
         "case_sensitive": True
     }

settings = Settings()
