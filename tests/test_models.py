import pytest
from src.domain.models import Event, SearchQuery, SearchResult, AnalysisResponse

def test_event_model():
    """Тест создания события"""
    event = Event(content="Тестовое событие", metadata={"source": "test"})
    assert event.content == "Тестовое событие"
    assert event.metadata["source"] == "test"

def test_search_query_model():
    """Тест поискового запроса"""
    query = SearchQuery(query="тест", limit=3)
    assert query.query == "тест"
    assert query.limit == 3

def test_search_query_validation():
    """Тест валидации лимита"""
    with pytest.raises(ValueError):
        SearchQuery(query="тест", limit=0)  # Должно упасть (limit >= 1)

def test_analysis_response_model():
    """Тест модели ответа анализа"""
    response = AnalysisResponse(
        query="тест",
        analysis="анализ",
        relevant_events=[]
    )
    assert response.query == "тест"
    assert isinstance(response.relevant_events, list)
