import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from src.main import app
from src.infrastructure.database.mongo_client import get_ratings_collection
from mongomock import MongoClient
from datetime import datetime

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def mock_mongo(monkeypatch):
    client = MongoClient()
    db = client.db
    collection = db.ratings
    
    def mock_get_collection():
        return collection
    
    monkeypatch.setattr("src.infrastructure.database.mongo_client.get_ratings_collection", mock_get_collection)
    return collection

def test_create_and_get_rating(test_client, mock_mongo):
    professional_id = str(uuid4())
    consumer_id = str(uuid4())
    payload = {
        "professional_id": professional_id,
        "consumer_id": consumer_id,
        "rate": 4,
        "description": "Muito bom!"
    }
    
    # Criar avaliação
    response = test_client.post("/ratings/", json=payload)
    assert response.status_code == 201
    created_rating = response.json()
    assert created_rating["professional_id"] == professional_id
    assert created_rating["consumer_id"] == consumer_id
    assert created_rating["rate"] == 4
    assert created_rating["description"] == "Muito bom!"
    assert "_id" in created_rating
    
    # Buscar avaliação criada
    rating_id = created_rating["_id"]
    response = test_client.get(f"/ratings/{rating_id}")
    assert response.status_code == 200
    retrieved_rating = response.json()
    assert retrieved_rating["_id"] == rating_id
    assert retrieved_rating["professional_id"] == professional_id
    assert retrieved_rating["consumer_id"] == consumer_id
    assert retrieved_rating["rate"] == 4
    assert retrieved_rating["description"] == "Muito bom!"

def test_create_rating_with_invalid_rate(test_client):
    payload = {
        "professional_id": str(uuid4()),
        "consumer_id": str(uuid4()),
        "rate": 6,  # Invalid rate
        "description": "Test"
    }
    response = test_client.post("/ratings/", json=payload)
    assert response.status_code == 422  # Validation error

def test_get_nonexistent_rating(test_client):
    response = test_client.get(f"/ratings/{uuid4()}")
    assert response.status_code == 404

def test_list_ratings_for_nonexistent_professional(test_client):
    response = test_client.get(f"/ratings/professional/{uuid4()}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 0
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["size"] == 10
    assert data["pages"] == 0

def test_list_ratings_by_professional(test_client, mock_mongo):
    professional_id = str(uuid4())
    
    # Criar algumas avaliações
    for i in range(3):
        payload = {
            "professional_id": professional_id,
            "consumer_id": str(uuid4()),
            "rate": i,
            "description": f"Test {i}"
        }
        response = test_client.post("/ratings/", json=payload)
        assert response.status_code == 201
    
    # Listar avaliações
    response = test_client.get(f"/ratings/professional/{professional_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["size"] == 10
    assert data["pages"] == 1
    assert all(r["professional_id"] == professional_id for r in data["items"])

def test_list_ratings_by_consumer(test_client, mock_mongo):
    consumer_id = str(uuid4())
    
    # Criar algumas avaliações
    for i in range(3):
        payload = {
            "professional_id": str(uuid4()),
            "consumer_id": consumer_id,
            "rate": i,
            "description": f"Test {i}"
        }
        response = test_client.post("/ratings/", json=payload)
        assert response.status_code == 201
    
    # Listar avaliações
    response = test_client.get(f"/ratings/consumer/{consumer_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["size"] == 10
    assert data["pages"] == 1
    assert all(r["consumer_id"] == consumer_id for r in data["items"])

def test_delete_rating(test_client, mock_mongo):
    # Criar uma avaliação
    payload = {
        "professional_id": str(uuid4()),
        "consumer_id": str(uuid4()),
        "rate": 5,
        "description": "Test rating"
    }
    response = test_client.post("/ratings/", json=payload)
    assert response.status_code == 201
    rating_id = response.json()["_id"]
    
    # Deletar avaliação
    response = test_client.delete(f"/ratings/{rating_id}")
    assert response.status_code == 204
    
    # Verificar se foi deletada
    response = test_client.get(f"/ratings/{rating_id}")
    assert response.status_code == 404 