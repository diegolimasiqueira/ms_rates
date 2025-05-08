import pytest
from src.infrastructure.database.mongo_config import MongoConfig
import os
from unittest.mock import patch

def test_get_uri():
    """Testa a obtenção da URI do MongoDB."""
    # Testa com variáveis de ambiente padrão
    with patch.dict(os.environ, {
        "MONGO_USER": "admin",
        "MONGO_PASSWORD": "password",
        "MONGO_HOST": "localhost",
        "MONGO_PORT": "27017",
        "MONGO_DB": "test"
    }, clear=True):
        uri = MongoConfig.get_uri()
        assert uri.startswith("mongodb://")
        assert "@" in uri
        assert ":" in uri
        assert "?" in uri
        assert "authSource=admin" in uri

    # Testa com variáveis de ambiente personalizadas
    with patch.dict(os.environ, {
        "MONGO_USER": "test_user",
        "MONGO_PASSWORD": "test_pass",
        "MONGO_HOST": "test_host",
        "MONGO_PORT": "27018",
        "MONGO_DB": "test_db"
    }, clear=True):
        uri = MongoConfig.get_uri()
        assert uri.startswith("mongodb://")
        assert "@" in uri
        assert ":" in uri
        assert "?" in uri
        assert "authSource=admin" in uri

def test_get_uri_no_env_vars():
    """Testa a obtenção da URI do MongoDB sem variáveis de ambiente."""
    with patch.dict(os.environ, {}, clear=True):
        uri = MongoConfig.get_uri()
        assert uri.startswith("mongodb://")
        assert "@" in uri
        assert ":" in uri
        assert "?" in uri
        assert "authSource=admin" in uri

def test_get_uri_missing_env_var():
    """Testa a obtenção da URI do MongoDB quando a variável MONGODB_URI não está definida."""
    with patch.dict(os.environ, {}, clear=True):
        with patch("src.infrastructure.database.mongo_config.load_dotenv", return_value=None):
            with pytest.raises(RuntimeError) as exc_info:
                MongoConfig.get_uri()
            assert "MONGODB_URI is not set in environment variables" in str(exc_info.value) 