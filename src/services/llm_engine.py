import httpx
from src.core.config import settings
from loguru import logger

class LLMEngine:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = settings.LLM_MODEL

    async def generate_analysis(self, query: str, context: str) -> str:
        """Генерация ответа на основе найденного контекста (RAG)"""
        if not self.api_key:
            logger.error("OPENROUTER_API_KEY не установлен!")
            return "Ошибка: API ключ не настроен."

        prompt = f"""Ты - ведущий аналитик системы EventHorizon. 
Используй предоставленные данные (Контекст), чтобы ответить на вопрос пользователя.
Если в контексте нет ответа, так и скажи.

Контекст:
{context}

Вопрос: {query}

Твой анализ (кратко, профессионально, по пунктам):"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/russo2100/EventHorizon", # Для OpenRouter
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.base_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return data['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"Ошибка LLM Engine: {e}")
            return f"Не удалось сгенерировать анализ из-за технической ошибки: {str(e)}"

# Создаем синглтон
llm_engine = LLMEngine()
