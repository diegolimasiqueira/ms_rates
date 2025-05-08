import pytest
from uuid import uuid4
from datetime import datetime, timezone, UTC
from src.application.services.rating_service import RatingService
from src.api.v1.schemas.rating import RatingCreate, RatingResponse
from src.domain.exceptions.base_exceptions import ValidationException, NotFoundException, DatabaseException
from unittest.mock import Mock

class MockRatingRepository:
    def __init__(self, should_raise_error=False):
        self.ratings = {}
        self.should_raise_error = should_raise_error

    def create_rating(self, rating):
        if self.should_raise_error:
            raise DatabaseException(message="Database error", details={"error": "Connection failed"})
        rating_id = str(uuid4())
        rating_dict = rating if isinstance(rating, dict) else rating.dict()
        rating_dict["_id"] = rating_id
        rating_dict["created_at"] = datetime.now(timezone.utc)
        self.ratings[rating_id] = rating_dict
        return rating_dict

    def get_rating_by_id(self, rating_id):
        if self.should_raise_error:
            raise DatabaseException(message="Database error", details={"error": "Connection failed"})
        return self.ratings.get(str(rating_id))

    def list_ratings_by_professional(self, professional_id, page, size):
        if self.should_raise_error:
            raise DatabaseException(message="Database error", details={"error": "Connection failed"})
        ratings = [
            r for r in self.ratings.values()
            if str(r["professional_id"]) == str(professional_id)
        ]
        start = (page - 1) * size
        end = start + size
        return ratings[start:end], len(ratings)

    def list_ratings_by_consumer(self, consumer_id, page, size):
        if self.should_raise_error:
            raise DatabaseException(message="Database error", details={"error": "Connection failed"})
        ratings = [
            r for r in self.ratings.values()
            if str(r["consumer_id"]) == str(consumer_id)
        ]
        start = (page - 1) * size
        end = start + size
        return ratings[start:end], len(ratings)

    def delete_rating(self, rating_id):
        if self.should_raise_error:
            raise DatabaseException(message="Database error", details={"error": "Connection failed"})
        if str(rating_id) not in self.ratings:
            return False
        del self.ratings[str(rating_id)]
        return True

@pytest.fixture
def mock_repository():
    return Mock()

@pytest.fixture
def service(mock_repository):
    return RatingService(mock_repository)

def test_create_and_get_rating():
    repo = MockRatingRepository()
    service = RatingService(repo)
    
    # Criar rating
    data = RatingCreate(
        professional_id=uuid4(),
        consumer_id=uuid4(),
        rate=5,
        description="Ótimo profissional!"
    )
    rating = service.create_rating(data)
    
    # Verificar se foi criado corretamente
    assert str(rating.professional_id) == str(data.professional_id)
    assert str(rating.consumer_id) == str(data.consumer_id)
    assert rating.rate == data.rate
    assert rating.description == data.description
    assert rating.id is not None

    # Buscar rating criado
    retrieved_rating = service.get_rating_by_id(rating.id)
    assert retrieved_rating.id == rating.id
    assert str(retrieved_rating.professional_id) == str(data.professional_id)
    assert str(retrieved_rating.consumer_id) == str(data.consumer_id)
    assert retrieved_rating.rate == data.rate
    assert retrieved_rating.description == data.description

def test_list_ratings_by_professional():
    repo = MockRatingRepository()
    service = RatingService(repo)
    prof_id = uuid4()
    
    # Criar algumas avaliações
    for i in range(3):
        data = RatingCreate(
            professional_id=prof_id,
            consumer_id=uuid4(),
            rate=i,
            description=None
        )
        service.create_rating(data)
    
    # Listar avaliações
    ratings, total = service.list_ratings_by_professional(prof_id, 1, 10)
    assert len(ratings) == 3
    assert total == 3
    assert all(str(r.professional_id) == str(prof_id) for r in ratings)

def test_list_ratings_by_consumer(service, mock_repository):
    """Testa a listagem de avaliações por consumidor."""
    consumer_id = uuid4()
    ratings = [
        {
            "_id": uuid4(),
            "professional_id": uuid4(),
            "consumer_id": consumer_id,
            "rate": 5,
            "description": "Test rating 1",
            "created_at": datetime.now(UTC)
        },
        {
            "_id": uuid4(),
            "professional_id": uuid4(),
            "consumer_id": consumer_id,
            "rate": 4,
            "description": "Test rating 2",
            "created_at": datetime.now(UTC)
        }
    ]
    mock_repository.list_ratings_by_consumer.return_value = (ratings, len(ratings))

    result, total = service.list_ratings_by_consumer(consumer_id)
    assert len(result) == 2
    assert total == 2
    assert all(isinstance(r, RatingResponse) for r in result)
    assert all(r.consumer_id == consumer_id for r in result)

def test_delete_rating():
    repo = MockRatingRepository()
    service = RatingService(repo)
    
    # Criar rating
    data = RatingCreate(
        professional_id=uuid4(),
        consumer_id=uuid4(),
        rate=5,
        description="Test rating"
    )
    rating = service.create_rating(data)
    
    # Deletar rating
    service.delete_rating(rating.id)
    
    # Verificar se foi deletado
    try:
        service.get_rating_by_id(rating.id)
        assert False, "Rating should not exist"
    except NotFoundException as e:
        assert "Rating not found" in str(e)

def test_create_rating_database_error():
    repo = MockRatingRepository(should_raise_error=True)
    service = RatingService(repo)
    
    data = RatingCreate(
        professional_id=uuid4(),
        consumer_id=uuid4(),
        rate=5,
        description="Test rating"
    )
    
    with pytest.raises(DatabaseException) as exc_info:
        service.create_rating(data)
    assert "Database error" in str(exc_info.value)

def test_get_rating_database_error():
    repo = MockRatingRepository(should_raise_error=True)
    service = RatingService(repo)
    
    with pytest.raises(DatabaseException) as exc_info:
        service.get_rating_by_id(uuid4())
    assert "Database error" in str(exc_info.value)

def test_list_ratings_by_professional_database_error():
    repo = MockRatingRepository(should_raise_error=True)
    service = RatingService(repo)
    
    with pytest.raises(DatabaseException) as exc_info:
        service.list_ratings_by_professional(uuid4(), 1, 10)
    assert "Database error" in str(exc_info.value)

def test_list_ratings_by_consumer_database_error():
    repo = MockRatingRepository(should_raise_error=True)
    service = RatingService(repo)
    
    with pytest.raises(DatabaseException) as exc_info:
        service.list_ratings_by_consumer(uuid4(), 1, 10)
    assert "Database error" in str(exc_info.value)

def test_delete_rating_database_error():
    repo = MockRatingRepository(should_raise_error=True)
    service = RatingService(repo)
    
    with pytest.raises(DatabaseException) as exc_info:
        service.delete_rating(uuid4())
    assert "Database error" in str(exc_info.value)

def test_get_rating_service_dependency():
    from src.infrastructure.repositories.rating_repository import get_rating_repository
    from src.application.services.rating_service import get_rating_service
    
    service = get_rating_service()
    assert isinstance(service, RatingService)
    assert service.repository is not None 