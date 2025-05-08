import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_startup_event():
    """Testa o evento de startup."""
    # O evento de startup é chamado automaticamente ao criar o TestClient
    response = client.get("/health/")
    assert response.status_code == 200

def test_shutdown_event():
    """Testa o evento de shutdown."""
    # O evento de shutdown é chamado automaticamente ao fechar o TestClient
    with TestClient(app) as client:
        response = client.get("/health/")
        assert response.status_code == 200 