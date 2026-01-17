from fastapi import FastAPI, HTTPException
from src.core.config import settings
from src.domain.models import EventCreate, SearchQuery
from src.services.knowledge_engine import engine
from loguru import logger

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

@app.on_event("startup")
async def startup_event():
    logger.info("EventHorizon API запускается...")

@app.post("/ingest/")
async def ingest_event(event: EventCreate):
    try:
        saved_event = engine.add_event(event)
        return {"status": "success", "id": saved_event.id}
    except Exception as e:
        logger.error(f"Ошибка при сохранении: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search/")
async def search_events(query: SearchQuery):
    results = engine.search(query.query, query.limit)
    # Если результатов нет, возвращаем понятный ответ
    if not results:
        return {"results": [], "message": "По вашему запросу ничего не найдено"}
    return {"results": results}


@app.get("/health")
async def health():
    return {"status": "alive", "engine": "txtai"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="127.0.0.1", port=8000, reload=True)
