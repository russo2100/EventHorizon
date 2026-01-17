import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_root_endpoint():
    """Тест корневого эндпоинта"""
    response = client.get("/")
    assert response.status_code == 200
    assert "EventHorizon" in response.json()["message"]

def test_health_endpoint():
    """Тест проверки здоровья системы"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "knowledge_engine" in data

def test_ingest_endpoint():
    """Тест добавления события"""
    event_data = {
        "content": "Тестовое событие для pytest",
        "metadata": {"source": "pytest", "type": "test"}
    }
    response = client.post("/ingest/", json=event_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "event_id" in data

def test_search_endpoint():
    """Тест поиска событий"""
    # Сначала добавим событие
    client.post("/ingest/", json={"content": "pytest поисковый тест", "metadata": {}})
    
    # Теперь ищем
    search_data = {"query": "pytest поиск", "limit": 5}
    response = client.post("/search/", json=search_data)
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)

def test_search_validation():
    """Тест валидации поискового запроса"""
    invalid_data = {"query": "тест", "limit": 0}  # limit должен быть >= 1
    response = client.post("/search/", json=invalid_data)
    assert response.status_code == 422  # Validation error
