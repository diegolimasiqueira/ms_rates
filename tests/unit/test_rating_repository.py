import pytest
from src.infrastructure.repositories.rating_repository import RatingRepositoryImpl
from src.domain.exceptions.base_exceptions import ValidationException, DatabaseException
from uuid import uuid4
from datetime import datetime, timezone
from pymongo.errors import WriteError, OperationFailure

@pytest.fixture
def repository():
    return RatingRepositoryImpl()

def test_create_rating(repository):
    """Testa a criação de uma avaliação."""
    rating_data = {
        "professional_id": str(uuid4()),
        "consumer_id": str(uuid4()),
        "rate": 5,
        "description": "Test rating"
    }
    
    created_rating = repository.create_rating(rating_data)
    assert created_rating["_id"] is not None
    assert created_rating["professional_id"] == rating_data["professional_id"]
    assert created_rating["consumer_id"] == rating_data["consumer_id"]
    assert created_rating["rate"] == rating_data["rate"]
    assert created_rating["description"] == rating_data["description"]
    assert isinstance(created_rating["created_at"], datetime)

def test_create_rating_validation_error(repository, monkeypatch):
    """Testa erro de validação ao criar avaliação."""
    def mock_insert_one(*args, **kwargs):
        raise WriteError("Validation error")
    
    monkeypatch.setattr(repository.collection, "insert_one", mock_insert_one)
    
    rating_data = {
        "professional_id": str(uuid4()),
        "consumer_id": str(uuid4()),
        "rate": 5,
        "description": "Test rating"
    }
    
    with pytest.raises(ValidationException):
        repository.create_rating(rating_data)

def test_create_rating_operation_error(repository, monkeypatch):
    """Testa erro de operação ao criar avaliação."""
    def mock_insert_one(*args, **kwargs):
        raise OperationFailure("Operation error")
    
    monkeypatch.setattr(repository.collection, "insert_one", mock_insert_one)
    
    rating_data = {
        "professional_id": str(uuid4()),
        "consumer_id": str(uuid4()),
        "rate": 5,
        "description": "Test rating"
    }
    
    with pytest.raises(DatabaseException):
        repository.create_rating(rating_data)

def test_get_rating_by_id(repository):
    """Testa a obtenção de uma avaliação por ID."""
    rating_data = {
        "professional_id": str(uuid4()),
        "consumer_id": str(uuid4()),
        "rate": 5,
        "description": "Test rating"
    }
    
    created_rating = repository.create_rating(rating_data)
    rating_id = created_rating["_id"]
    
    retrieved_rating = repository.get_rating_by_id(rating_id)
    assert retrieved_rating is not None
    assert str(retrieved_rating["_id"]) == str(rating_id)
    assert str(retrieved_rating["professional_id"]) == rating_data["professional_id"]
    assert str(retrieved_rating["consumer_id"]) == rating_data["consumer_id"]
    assert retrieved_rating["rate"] == rating_data["rate"]
    assert retrieved_rating["description"] == rating_data["description"]

def test_get_nonexistent_rating(repository):
    """Testa a obtenção de uma avaliação inexistente."""
    rating_id = str(uuid4())
    retrieved_rating = repository.get_rating_by_id(rating_id)
    assert retrieved_rating is None

def test_list_ratings_by_professional(repository):
    """Testa a listagem de avaliações por profissional."""
    professional_id = str(uuid4())
    
    # Cria algumas avaliações
    for i in range(3):
        rating_data = {
            "professional_id": professional_id,
            "consumer_id": str(uuid4()),
            "rate": i + 1,
            "description": f"Test rating {i}"
        }
        repository.create_rating(rating_data)
    
    # Lista as avaliações
    ratings, total = repository.list_ratings_by_professional(professional_id, page=1, size=10)
    assert len(ratings) == 3
    assert total == 3
    
    # Verifica paginação
    ratings, total = repository.list_ratings_by_professional(professional_id, page=1, size=2)
    assert len(ratings) == 2
    assert total == 3

def test_list_ratings_by_consumer(repository):
    """Testa a listagem de avaliações por consumidor."""
    consumer_id = str(uuid4())
    
    # Cria algumas avaliações
    for i in range(3):
        rating_data = {
            "professional_id": str(uuid4()),
            "consumer_id": consumer_id,
            "rate": i + 1,
            "description": f"Test rating {i}"
        }
        repository.create_rating(rating_data)
    
    # Lista as avaliações
    ratings, total = repository.list_ratings_by_consumer(consumer_id, page=1, size=10)
    assert len(ratings) == 3
    assert total == 3
    
    # Verifica paginação
    ratings, total = repository.list_ratings_by_consumer(consumer_id, page=1, size=2)
    assert len(ratings) == 2
    assert total == 3

def test_delete_rating(repository):
    """Testa a exclusão de uma avaliação."""
    rating_data = {
        "professional_id": str(uuid4()),
        "consumer_id": str(uuid4()),
        "rate": 5,
        "description": "Test rating"
    }
    
    created_rating = repository.create_rating(rating_data)
    rating_id = created_rating["_id"]
    
    # Deleta a avaliação
    deleted = repository.delete_rating(rating_id)
    assert deleted is True
    
    # Verifica se foi realmente deletada
    retrieved_rating = repository.get_rating_by_id(rating_id)
    assert retrieved_rating is None

def test_delete_nonexistent_rating(repository):
    """Testa a exclusão de uma avaliação inexistente."""
    rating_id = str(uuid4())
    deleted = repository.delete_rating(rating_id)
    assert deleted is False

def test_list_ratings_by_professional_pagination(repository):
    """Testa a paginação na listagem de avaliações por profissional."""
    professional_id = str(uuid4())
    
    # Cria 15 avaliações
    for i in range(15):
        rating_data = {
            "professional_id": professional_id,
            "consumer_id": str(uuid4()),
            "rate": 5,
            "description": f"Test rating {i}"
        }
        repository.create_rating(rating_data)
    
    # Testa primeira página
    ratings, total = repository.list_ratings_by_professional(professional_id, page=1, size=10)
    assert len(ratings) == 10
    assert total == 15
    
    # Testa segunda página
    ratings, total = repository.list_ratings_by_professional(professional_id, page=2, size=10)
    assert len(ratings) == 5
    assert total == 15

def test_list_ratings_by_consumer_pagination(repository):
    """Testa a paginação na listagem de avaliações por consumidor."""
    consumer_id = str(uuid4())
    
    # Cria 15 avaliações
    for i in range(15):
        rating_data = {
            "professional_id": str(uuid4()),
            "consumer_id": consumer_id,
            "rate": 5,
            "description": f"Test rating {i}"
        }
        repository.create_rating(rating_data)
    
    # Testa primeira página
    ratings, total = repository.list_ratings_by_consumer(consumer_id, page=1, size=10)
    assert len(ratings) == 10
    assert total == 15
    
    # Testa segunda página
    ratings, total = repository.list_ratings_by_consumer(consumer_id, page=2, size=10)
    assert len(ratings) == 5
    assert total == 15

def test_list_ratings_by_professional_empty(repository):
    """Testa a listagem de avaliações para um profissional sem avaliações."""
    professional_id = str(uuid4())
    ratings, total = repository.list_ratings_by_professional(professional_id)
    assert len(ratings) == 0
    assert total == 0

def test_list_ratings_by_consumer_empty(repository):
    """Testa a listagem de avaliações para um consumidor sem avaliações."""
    consumer_id = str(uuid4())
    ratings, total = repository.list_ratings_by_consumer(consumer_id)
    assert len(ratings) == 0
    assert total == 0

def test_delete_rating_error_handling(repository):
    """Testa o tratamento de erros ao excluir uma avaliação."""
    # Tenta excluir uma avaliação inexistente
    rating_id = str(uuid4())
    deleted = repository.delete_rating(rating_id)
    assert deleted is False

def test_create_rating_operation_failure(repository):
    """Testa o tratamento de erro de operação ao criar uma avaliação."""
    from pymongo.errors import OperationFailure
    
    def mock_insert_one(*args, **kwargs):
        raise OperationFailure("Erro de operação")
    
    # Salva o método original
    original_insert_one = repository.collection.insert_one
    
    try:
        # Substitui o método por um mock
        repository.collection.insert_one = mock_insert_one
        
        rating_data = {
            "professional_id": str(uuid4()),
            "consumer_id": str(uuid4()),
            "rate": 5,
            "description": "Test rating"
        }
        
        with pytest.raises(DatabaseException) as exc_info:
            repository.create_rating(rating_data)
        assert "Database operation failed" in str(exc_info.value)
    finally:
        # Restaura o método original
        repository.collection.insert_one = original_insert_one

def test_create_rating_unexpected_error(repository):
    """Testa o tratamento de erro inesperado ao criar uma avaliação."""
    def mock_insert_one(*args, **kwargs):
        raise RuntimeError("Erro inesperado")
    
    # Salva o método original
    original_insert_one = repository.collection.insert_one
    
    try:
        # Substitui o método por um mock
        repository.collection.insert_one = mock_insert_one
        
        rating_data = {
            "professional_id": str(uuid4()),
            "consumer_id": str(uuid4()),
            "rate": 5,
            "description": "Test rating"
        }
        
        with pytest.raises(DatabaseException) as exc_info:
            repository.create_rating(rating_data)
        assert "Failed to create rating" in str(exc_info.value)
    finally:
        # Restaura o método original
        repository.collection.insert_one = original_insert_one

def test_get_rating_by_id_error(repository):
    """Testa o tratamento de erro ao buscar uma avaliação por ID."""
    def mock_find_one(*args, **kwargs):
        raise RuntimeError("Erro inesperado")
    
    # Salva o método original
    original_find_one = repository.collection.find_one
    
    try:
        # Substitui o método por um mock
        repository.collection.find_one = mock_find_one
        
        with pytest.raises(DatabaseException) as exc_info:
            repository.get_rating_by_id(uuid4())
        assert "Failed to fetch rating" in str(exc_info.value)
    finally:
        # Restaura o método original
        repository.collection.find_one = original_find_one

def test_list_ratings_by_professional_error(repository):
    """Testa o tratamento de erro ao listar avaliações por profissional."""
    def mock_count_documents(*args, **kwargs):
        raise RuntimeError("Erro inesperado")
    
    # Salva o método original
    original_count_documents = repository.collection.count_documents
    
    try:
        # Substitui o método por um mock
        repository.collection.count_documents = mock_count_documents
        
        with pytest.raises(DatabaseException) as exc_info:
            repository.list_ratings_by_professional(uuid4())
        assert "Failed to list ratings" in str(exc_info.value)
    finally:
        # Restaura o método original
        repository.collection.count_documents = original_count_documents

def test_list_ratings_by_consumer_error(repository):
    """Testa o tratamento de erro ao listar avaliações por consumidor."""
    def mock_count_documents(*args, **kwargs):
        raise RuntimeError("Erro inesperado")
    
    # Salva o método original
    original_count_documents = repository.collection.count_documents
    
    try:
        # Substitui o método por um mock
        repository.collection.count_documents = mock_count_documents
        
        with pytest.raises(DatabaseException) as exc_info:
            repository.list_ratings_by_consumer(uuid4())
        assert "Failed to list ratings" in str(exc_info.value)
    finally:
        # Restaura o método original
        repository.collection.count_documents = original_count_documents

def test_delete_rating_error(repository):
    """Testa o tratamento de erro ao excluir uma avaliação."""
    def mock_delete_one(*args, **kwargs):
        raise RuntimeError("Erro inesperado")
    
    # Salva o método original
    original_delete_one = repository.collection.delete_one
    
    try:
        # Substitui o método por um mock
        repository.collection.delete_one = mock_delete_one
        
        with pytest.raises(DatabaseException) as exc_info:
            repository.delete_rating(uuid4())
        assert "Failed to delete rating" in str(exc_info.value)
    finally:
        # Restaura o método original
        repository.collection.delete_one = original_delete_one 