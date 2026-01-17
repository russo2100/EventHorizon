from fastapi import FastAPI, HTTPException
from loguru import logger
from src.domain.models import Event, SearchQuery, SearchResult, AnalysisResponse
from src.services.knowledge_engine import knowledge_engine
from src.services.llm_engine import llm_engine

app = FastAPI(
    title="EventHorizon API",
    description="Локальная платформа для анализа и хранения событий с семантическим поиском и LLM-аналитикой",
    version="2.0.0"
)

@app.get("/")
async def root():
    return {"message": "EventHorizon API v2.0 - Ready for Analysis"}

@app.get("/health")
async def health():
    """Проверка работоспособности системы"""
    return {
        "status": "healthy",
        "knowledge_engine": "active",
        "llm_engine": "active" if llm_engine.api_key else "no_api_key"
    }

@app.post("/ingest/")
async def ingest_event(event: Event):
    """Сохранение события в векторную базу"""
    try:
        event_id = knowledge_engine.add_event(event.content, event.metadata or {})
        logger.info(f"Событие добавлено: ID={event_id}")
        return {"status": "success", "event_id": event_id}
    except Exception as e:
        logger.error(f"Ошибка при добавлении события: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search/", response_model=list[SearchResult])
async def search_events(query: SearchQuery):
    """Семантический поиск событий"""
    try:
        results = knowledge_engine.search(query.query, limit=query.limit)
        logger.info(f"Найдено {len(results)} событий по запросу: {query.query}")
        return results
    except Exception as e:
        logger.error(f"Ошибка поиска: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/", response_model=AnalysisResponse)
async def analyze_query(query: SearchQuery):
    """
    RAG-пайплайн: поиск релевантных событий + генерация аналитического отчета через LLM
    
    Этапы:
    1. Семантический поиск по базе событий
    2. Формирование контекста из найденных событий
    3. Генерация анализа через OpenRouter LLM
    """
    try:
        # Шаг 1: Поиск релевантных событий
        results = knowledge_engine.search(query.query, limit=query.limit)
        
        if not results:
            return AnalysisResponse(
                query=query.query,
                analysis="В базе данных не найдено событий, релевантных вашему запросу. Попробуйте переформулировать или добавьте больше данных.",
                relevant_events=[]
            )
        
        # Шаг 2: Формирование контекста для LLM
        context = "\n\n".join([
            f"Событие {i+1} (релевантность {r.score:.2f}):\n{r.text}" 
            for i, r in enumerate(results)
        ])
        
        # Шаг 3: Генерация анализа
        analysis = await llm_engine.generate_analysis(query.query, context)
        
        logger.info(f"Анализ сгенерирован для запроса: {query.query}")
        
        return AnalysisResponse(
            query=query.query,
            analysis=analysis,
            relevant_events=results
        )
        
    except Exception as e:
        logger.error(f"Ошибка в RAG-пайплайне: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка анализа: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

