import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "EventHorizon"
    VERSION: str = "0.1.0"
    
    # ВАЖНО: Мы задаем путь ОТНОСИТЕЛЬНО текущей рабочей директории.
    # Это позволяет избежать передачи полного пути с кириллицей в C++ библиотеки.
    # Точка (.) означает "текущая папка запуска".
    INDEX_PATH_STR: str = "data/index"
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Создаем папку (Python умеет работать с кириллицей, он создаст)
os.makedirs(settings.INDEX_PATH_STR, exist_ok=True)
