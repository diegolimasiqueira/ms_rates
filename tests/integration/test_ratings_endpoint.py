import pytest
import pytest_asyncio
from uuid import uuid4
from src.main import app
from src.infrastructure.database.mongo_client import get_ratings_collection
from mongomock import MongoClient
from datetime import datetime
from httpx import AsyncClient, ASGITransport
from src.infrastructure.repositories.rating_repository import get_rating_repository
from src.domain.exceptions.base_exceptions import DatabaseException

@pytest_asyncio.fixture
async def test_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.fixture
def mock_mongo(monkeypatch):
    client = MongoClient()
    db = client.db
    collection = db.ratings
    
    def mock_get_collection():
        return collection
    
    monkeypatch.setattr("src.infrastructure.database.mongo_client.get_ratings_collection", mock_get_collection)
    return collection

@pytest.mark.asyncio
async def test_create_and_get_rating(test_client, mock_mongo):
    professional_id = str(uuid4())
    consumer_id = str(uuid4())
    payload = {
        "professional_id": professional_id,
        "consumer_id": consumer_id,
        "rate": 4,
        "description": "Muito bom!"
    }
    
    # Criar avaliação
    response = await test_client.post("/ratings/", json=payload)
    assert response.status_code == 201
    created_rating = response.json()
    assert created_rating["professional_id"] == professional_id
    assert created_rating["consumer_id"] == consumer_id
    assert created_rating["rate"] == 4
    assert created_rating["description"] == "Muito bom!"
    assert "_id" in created_rating
    
    # Buscar avaliação criada
    rating_id = created_rating["_id"]
    response = await test_client.get(f"/ratings/{rating_id}")
    assert response.status_code == 200
    retrieved_rating = response.json()
    assert retrieved_rating["_id"] == rating_id
    assert retrieved_rating["professional_id"] == professional_id
    assert retrieved_rating["consumer_id"] == consumer_id
    assert retrieved_rating["rate"] == 4
    assert retrieved_rating["description"] == "Muito bom!"

@pytest.mark.asyncio
async def test_create_rating_with_invalid_rate(test_client):
    payload = {
        "professional_id": str(uuid4()),
        "consumer_id": str(uuid4()),
        "rate": 6,  # Invalid rate
        "description": "Test"
    }
    response = await test_client.post("/ratings/", json=payload)
    assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
async def test_get_nonexistent_rating(test_client):
    response = await test_client.get(f"/ratings/{uuid4()}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_list_ratings_for_nonexistent_professional(test_client):
    response = await test_client.get(f"/ratings/professional/{uuid4()}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 0
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["size"] == 10
    assert data["pages"] == 0

@pytest.mark.asyncio
async def test_list_ratings_by_professional(test_client, mock_mongo):
    professional_id = str(uuid4())
    
    # Criar algumas avaliações
    for i in range(3):
        payload = {
            "professional_id": professional_id,
            "consumer_id": str(uuid4()),
            "rate": i,
            "description": f"Test {i}"
        }
        response = await test_client.post("/ratings/", json=payload)
        assert response.status_code == 201
    
    # Listar avaliações
    response = await test_client.get(f"/ratings/professional/{professional_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["size"] == 10
    assert data["pages"] == 1
    assert all(r["professional_id"] == professional_id for r in data["items"])

@pytest.mark.asyncio
async def test_list_ratings_by_consumer(test_client, mock_mongo):
    consumer_id = str(uuid4())
    
    # Criar algumas avaliações
    for i in range(3):
        payload = {
            "professional_id": str(uuid4()),
            "consumer_id": consumer_id,
            "rate": i,
            "description": f"Test {i}"
        }
        response = await test_client.post("/ratings/", json=payload)
        assert response.status_code == 201
    
    # Listar avaliações
    response = await test_client.get(f"/ratings/consumer/{consumer_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["size"] == 10
    assert data["pages"] == 1
    assert all(r["consumer_id"] == consumer_id for r in data["items"])

@pytest.mark.asyncio
async def test_delete_rating(test_client, mock_mongo):
    # Criar uma avaliação
    payload = {
        "professional_id": str(uuid4()),
        "consumer_id": str(uuid4()),
        "rate": 5,
        "description": "Test rating"
    }
    response = await test_client.post("/ratings/", json=payload)
    assert response.status_code == 201
    rating_id = response.json()["_id"]
    
    # Deletar avaliação
    response = await test_client.delete(f"/ratings/{rating_id}")
    assert response.status_code == 204
    
    # Verificar se foi deletada
    response = await test_client.get(f"/ratings/{rating_id}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_rating_invalid_rate():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/ratings/",
            json={
                "professional_id": str(uuid4()),
                "consumer_id": str(uuid4()),
                "rate": 6,  # Invalid rate (should be 1-5)
                "description": "Test rating"
            }
        )
        assert response.status_code == 422
        assert "rate" in response.json()["detail"][0]["loc"]

@pytest.mark.asyncio
async def test_create_rating_missing_fields():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/ratings/",
            json={
                "professional_id": str(uuid4()),
                # Missing consumer_id
                "rate": 5,
                "description": "Test rating"
            }
        )
        assert response.status_code == 422
        assert "consumer_id" in response.json()["detail"][0]["loc"]

@pytest.mark.asyncio
async def test_list_ratings_invalid_pagination():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            f"/ratings/professional/{uuid4()}?page=0&size=10"
        )
        assert response.status_code == 422
        assert "page" in response.json()["detail"][0]["loc"]

@pytest.mark.asyncio
async def test_list_ratings_invalid_size():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            f"/ratings/professional/{uuid4()}?page=1&size=0"
        )
        assert response.status_code == 422
        assert "size" in response.json()["detail"][0]["loc"]

@pytest.mark.asyncio
async def test_delete_rating_invalid_id():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.delete("/ratings/invalid-uuid")
        assert response.status_code == 422
        assert "id" in response.json()["detail"][0]["loc"]

@pytest.mark.asyncio
async def test_get_rating_invalid_id():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/ratings/invalid-uuid")
        assert response.status_code == 422
        assert "id" in response.json()["detail"][0]["loc"]

@pytest.mark.asyncio
async def test_list_ratings_empty_results():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            f"/ratings/professional/{uuid4()}?page=1&size=10"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["size"] == 10
        assert data["pages"] == 0 