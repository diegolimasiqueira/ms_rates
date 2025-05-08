import pytest
from fastapi.testclient import TestClient
from src.main import app
from fastapi.exceptions import RequestValidationError
from pymongo.errors import PyMongoError
from uuid import UUID, uuid4
from src.api.v1.schemas.rating import RatingCreate

client = TestClient(app)

# Gera UUIDs versão 4 válidos
UUID1 = str(uuid4())
UUID2 = str(uuid4())

def test_request_validation_error():
    # Envia um campo inválido para forçar o RequestValidationError
    response = client.post("/ratings/", json={"rate": 999})
    assert response.status_code == 422
    assert "Invalid request data" in response.text or "value_error" in response.text

def test_pymongo_error(monkeypatch):
    # Mocka o método do serviço para lançar PyMongoError
    from src.application.services.rating_service import RatingService
    def raise_pymongo(*args, **kwargs):
        raise PyMongoError("Erro fake do Mongo")
    monkeypatch.setattr(RatingService, "create_rating", raise_pymongo)
    
    # Dados válidos conforme o schema
    valid_data = {
        "professional_id": UUID1,
        "consumer_id": UUID2,
        "rate": 5,
        "description": "desc"
    }
    
    response = client.post("/ratings/", json=valid_data)
    assert response.status_code == 500
    assert "An error occurred while accessing the database" in response.text

def test_unexpected_error(monkeypatch):
    # Mocka o método do serviço para lançar um erro genérico
    from src.application.services.rating_service import RatingService
    def raise_runtime(*args, **kwargs):
        raise RuntimeError("Erro inesperado")
    monkeypatch.setattr(RatingService, "create_rating", raise_runtime)
    
    # Dados válidos conforme o schema
    valid_data = {
        "professional_id": UUID1,
        "consumer_id": UUID2,
        "rate": 5,
        "description": "desc"
    }
    
    response = client.post("/ratings/", json=valid_data)
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.text 