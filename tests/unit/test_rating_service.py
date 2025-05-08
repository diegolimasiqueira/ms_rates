import pytest
from uuid import uuid4
from datetime import datetime
from src.application.services.rating_service import RatingService
from src.api.v1.schemas.rating import RatingCreate

class MockRatingRepository:
    def __init__(self):
        self.ratings = {}

    def create_rating(self, rating):
        rating_id = rating["_id"]
        self.ratings[rating_id] = rating
        return rating

    def get_rating_by_id(self, rating_id):
        return self.ratings.get(rating_id)

    def list_ratings_by_professional(self, professional_id):
        return [r for r in self.ratings.values() if r["professional_id"] == professional_id]

def test_create_and_get_rating():
    repo = MockRatingRepository()
    service = RatingService(repo)
    data = RatingCreate(
        professional_id=uuid4(),
        consumer_id=uuid4(),
        rate=5,
        description="Ótimo profissional!"
    )
    rating = service.create_rating(data)
    assert rating.rate == 5
    assert rating.id is not None
    fetched = service.get_rating_by_id(rating.id)
    assert fetched is not None
    assert fetched.id == rating.id

def test_list_ratings_by_professional():
    repo = MockRatingRepository()
    service = RatingService(repo)
    prof_id = uuid4()
    for i in range(3):
        data = RatingCreate(
            professional_id=prof_id,
            consumer_id=uuid4(),
            rate=i,
            description=None
        )
        service.create_rating(data)
    ratings = service.list_ratings_by_professional(prof_id)
    assert len(ratings) == 3 