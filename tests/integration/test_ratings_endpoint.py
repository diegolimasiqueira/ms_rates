import pytest
from fastapi.testclient import TestClient
from src.main import app
from uuid import uuid4
import mongomock
from src.infrastructure.database.mongo_client import get_ratings_collection, set_mongo_client
import bson

# Mock MongoDB collection
@pytest.fixture
def mock_mongo():
    client = mongomock.MongoClient()
    db = client["easyprofind"]
    coll = db["ratings"]
    set_mongo_client(client)
    return coll

@pytest.fixture
def test_client(mock_mongo):
    return TestClient(app)

def test_create_and_get_rating(test_client, mock_mongo):
    professional_id = str(uuid4())
    consumer_id = str(uuid4())
    payload = {
        "professional_id": professional_id,
        "consumer_id": consumer_id,
        "rate": 4,
        "description": "Muito bom!"
    }
    # Cria avaliação
    response = test_client.post("/ratings/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["rate"] == 4
    rating_id = data["_id"]

    # Busca avaliação por ID
    response = test_client.get(f"/ratings/{rating_id}")
    assert response.status_code == 200
    data2 = response.json()
    assert data2["_id"] == rating_id

    # Lista avaliações do profissional
    response = test_client.get(f"/ratings/professional/{professional_id}")
    assert response.status_code == 200
    ratings = response.json()
    assert any(r["_id"] == rating_id for r in ratings)

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
    assert response.json() == [] 