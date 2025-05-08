import pytest
from fastapi.testclient import TestClient
from src.main import app
from fastapi.exceptions import RequestValidationError
from pymongo.errors import PyMongoError, WriteError, OperationFailure
from uuid import UUID, uuid4
from src.api.v1.schemas.rating import RatingCreate
from src.domain.exceptions.base_exceptions import BaseAPIException, ValidationException, DatabaseException

client = TestClient(app)

# Gera UUIDs versão 4 válidos
UUID1 = str(uuid4())
UUID2 = str(uuid4())

def test_request_validation_error():
    # Envia um campo inválido para forçar o RequestValidationError
    response = client.post("/ratings/", json={"rate": 999})
    assert response.status_code == 422
    assert "Invalid request data" in response.text or "value_error" in response.text

def test_pymongo_error():
    # Testa o handler de PyMongoError
    from src.application.services.rating_service import RatingService
    from pymongo.errors import PyMongoError

    def raise_pymongo(*args, **kwargs):
        raise PyMongoError("Erro no MongoDB")

    with pytest.MonkeyPatch.context() as m:
        m.setattr(RatingService, "create_rating", raise_pymongo)

        valid_data = {
            "professional_id": UUID1,
            "consumer_id": UUID2,
            "rate": 5,
            "description": "desc"
        }

        response = client.post("/ratings/", json=valid_data)
        assert response.status_code == 500
        response_data = response.json()
        assert "detail" in response_data
        assert response_data["detail"]["message"] == "An error occurred while accessing the database"
        assert response_data["detail"]["details"]["error"] == "Erro no MongoDB"

def test_unexpected_error():
    # Testa o handler de exceções inesperadas
    from src.application.services.rating_service import RatingService

    def raise_unexpected(*args, **kwargs):
        raise RuntimeError("Erro inesperado")

    with pytest.MonkeyPatch.context() as m:
        m.setattr(RatingService, "create_rating", raise_unexpected)

        valid_data = {
            "professional_id": UUID1,
            "consumer_id": UUID2,
            "rate": 5,
            "description": "desc"
        }

        response = client.post("/ratings/", json=valid_data)
        assert response.status_code == 500
        response_data = response.json()
        assert "detail" in response_data
        assert response_data["detail"]["message"] == "An unexpected error occurred"
        assert response_data["detail"]["details"]["error"] == "Erro inesperado"

def test_write_error(monkeypatch):
    # Mocka o método do serviço para lançar WriteError
    from src.application.services.rating_service import RatingService
    def raise_write_error(*args, **kwargs):
        raise WriteError("Erro de validação do Mongo")
    monkeypatch.setattr(RatingService, "create_rating", raise_write_error)
    
    valid_data = {
        "professional_id": UUID1,
        "consumer_id": UUID2,
        "rate": 5,
        "description": "desc"
    }
    
    response = client.post("/ratings/", json=valid_data)
    assert response.status_code == 500
    assert "An error occurred while accessing the database" in response.text

def test_operation_failure(monkeypatch):
    # Mocka o método do serviço para lançar OperationFailure
    from src.application.services.rating_service import RatingService
    def raise_operation_failure(*args, **kwargs):
        raise OperationFailure("Erro de operação do Mongo")
    monkeypatch.setattr(RatingService, "create_rating", raise_operation_failure)
    
    valid_data = {
        "professional_id": UUID1,
        "consumer_id": UUID2,
        "rate": 5,
        "description": "desc"
    }
    
    response = client.post("/ratings/", json=valid_data)
    assert response.status_code == 500
    assert "An error occurred while accessing the database" in response.text

def test_base_api_exception():
    # Testa o handler de BaseAPIException
    from src.application.services.rating_service import RatingService
    def raise_validation(*args, **kwargs):
        raise ValidationException("Erro de validação", {"field": "test"})

    with pytest.MonkeyPatch.context() as m:
        m.setattr(RatingService, "create_rating", raise_validation)

        valid_data = {
            "professional_id": UUID1,
            "consumer_id": UUID2,
            "rate": 5,
            "description": "desc"
        }

        response = client.post("/ratings/", json=valid_data)
        assert response.status_code == 500
        response_data = response.json()
        assert "detail" in response_data
        assert response_data["detail"]["message"] == "An unexpected error occurred"
        assert response_data["detail"]["details"]["error"] == "Erro de validação" 