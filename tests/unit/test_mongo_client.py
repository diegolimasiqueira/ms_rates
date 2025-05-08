import pytest
from src.infrastructure.database.mongo_client import get_mongo_client, get_ratings_collection, set_mongo_client
from pymongo import MongoClient
from pymongo.errors import CollectionInvalid, WriteError
import mongomock
from datetime import datetime, timezone
from uuid import uuid4

def test_get_mongo_client():
    """Testa a obtenção do cliente MongoDB."""
    client = get_mongo_client()
    assert isinstance(client, (MongoClient, mongomock.MongoClient))

def test_get_ratings_collection():
    """Testa a obtenção da coleção de ratings."""
    collection = get_ratings_collection()
    assert collection.name == "ratings"
    
    # Verifica se os índices foram criados
    indexes = collection.list_indexes()
    index_names = [index["name"] for index in indexes]
    assert "professional_id_1" in index_names
    assert "consumer_id_1" in index_names
    assert "professional_id_-1_created_at_-1" in index_names

def test_collection_validation():
    """Testa a validação da coleção."""
    collection = get_ratings_collection()
    
    # Testa inserção de documento válido
    valid_doc = {
        "_id": str(uuid4()),
        "professional_id": str(uuid4()),
        "consumer_id": str(uuid4()),
        "rate": 5,
        "description": "Test rating",
        "created_at": datetime.now(timezone.utc)
    }
    collection.insert_one(valid_doc)
    
    # Testa inserção de documento inválido
    invalid_doc = {
        "_id": str(uuid4()),
        "professional_id": str(uuid4()),
        "consumer_id": str(uuid4()),
        "rate": 6,  # Rate maior que 5
        "description": "Test rating",
        "created_at": datetime.now(timezone.utc)
    }
    with pytest.raises(WriteError):
        collection.insert_one(invalid_doc)

def test_create_indexes():
    """Testa a criação de índices."""
    collection = get_ratings_collection()
    
    # Verifica se os índices foram criados
    indexes = list(collection.list_indexes())
    assert len(indexes) >= 3  # _id (padrão), professional_id e consumer_id
    
    # Verifica o índice de professional_id
    professional_index = next(idx for idx in indexes if "professional_id" in idx["key"])
    assert professional_index["key"]["professional_id"] == 1
    
    # Verifica o índice de consumer_id
    consumer_index = next(idx for idx in indexes if "consumer_id" in idx["key"])
    assert consumer_index["key"]["consumer_id"] == 1

def test_collection_validation_schema():
    """Testa o schema de validação da coleção."""
    collection = get_ratings_collection()
    
    # Testa inserção de documento com rate inválido
    invalid_doc = {
        "_id": str(uuid4()),
        "professional_id": str(uuid4()),
        "consumer_id": str(uuid4()),
        "rate": 6,  # Rate maior que 5
        "description": "Test rating",
        "created_at": datetime.now(timezone.utc)
    }
    with pytest.raises(WriteError) as exc_info:
        collection.insert_one(invalid_doc)
    assert "Document failed validation" in str(exc_info.value)
    
    # Testa inserção de documento sem campo obrigatório
    invalid_doc = {
        "_id": str(uuid4()),
        "professional_id": str(uuid4()),
        # consumer_id faltando
        "rate": 5,
        "description": "Test rating",
        "created_at": datetime.now(timezone.utc)
    }
    with pytest.raises(WriteError) as exc_info:
        collection.insert_one(invalid_doc)
    assert "Document failed validation" in str(exc_info.value)

def test_create_collection_with_validation():
    """Testa a criação da coleção com validação."""
    collection = get_ratings_collection()
    
    # Verifica se a coleção foi criada
    assert collection.name == "ratings"
    
    # Verifica se o schema de validação foi aplicado
    options = collection.options()
    assert "validator" in options
    assert "$jsonSchema" in options["validator"]
    
    # Verifica os campos obrigatórios
    required_fields = options["validator"]["$jsonSchema"]["required"]
    assert "_id" in required_fields
    assert "professional_id" in required_fields
    assert "consumer_id" in required_fields
    assert "rate" in required_fields
    assert "created_at" in required_fields

def test_create_collection_with_mongomock():
    """Testa a criação da coleção usando mongomock."""
    import mongomock
    client = mongomock.MongoClient()
    set_mongo_client(client)
    
    collection = get_ratings_collection()
    
    # Verifica se a coleção foi criada
    assert collection.name == "ratings"
    
    # Verifica se os índices foram criados
    indexes = list(collection.list_indexes())
    assert len(indexes) >= 3  # _id (padrão), professional_id e consumer_id

def test_create_collection_invalid():
    """Testa a criação da coleção quando ela já existe."""
    collection = get_ratings_collection()
    
    # Tenta criar a coleção novamente
    collection = get_ratings_collection()
    
    # Verifica se a coleção ainda existe
    assert collection.name == "ratings"

def test_create_collection_with_validation_and_indexes():
    """Testa a criação da coleção com validação e índices."""
    collection = get_ratings_collection()
    
    # Verifica se a coleção foi criada
    assert collection.name == "ratings"
    
    # Verifica se os índices foram criados
    indexes = list(collection.list_indexes())
    assert len(indexes) >= 4  # _id (padrão), professional_id, consumer_id e (professional_id, created_at)
    
    # Verifica o índice de professional_id
    professional_index = next(idx for idx in indexes if "professional_id" in idx["key"] and len(idx["key"]) == 1)
    assert professional_index["key"]["professional_id"] == 1
    
    # Verifica o índice de consumer_id
    consumer_index = next(idx for idx in indexes if "consumer_id" in idx["key"])
    assert consumer_index["key"]["consumer_id"] == 1
    
    # Verifica o índice composto (professional_id, created_at)
    compound_index = next(idx for idx in indexes if "professional_id" in idx["key"] and "created_at" in idx["key"])
    assert compound_index["key"]["professional_id"] == -1
    assert compound_index["key"]["created_at"] == -1 