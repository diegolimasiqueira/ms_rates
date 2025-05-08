import logging
from src.domain.interfaces.rating_repository import RatingRepository
from src.api.v1.schemas.rating import RatingCreate, RatingResponse
from src.domain.exceptions.base_exceptions import ValidationException, NotFoundException, DatabaseException
from uuid import UUID, uuid4
from datetime import datetime, UTC
from typing import List, Optional
from fastapi import Depends
from src.infrastructure.repositories.rating_repository import RatingRepositoryImpl, get_rating_repository

logger = logging.getLogger(__name__)

class RatingService:
    """Service layer for rating operations."""
    def __init__(self, repository: RatingRepository):
        self.repository = repository

    def create_rating(self, rating_data: RatingCreate) -> RatingResponse:
        """Create a new rating."""
        try:
            logger.info(f"Creating rating for professional {rating_data.professional_id}")
            rating_dict = rating_data.dict()
            # Cria o rating e obtém os dados completos
            created_rating = self.repository.create_rating(rating_dict)
            logger.info(f"Rating created successfully with ID {created_rating['_id']}")
            return RatingResponse(**created_rating)
        except Exception as e:
            logger.error(f"Error creating rating: {str(e)}")
            raise ValidationException(
                message="Failed to create rating",
                details={"error": str(e)}
            )

    def get_rating_by_id(self, rating_id: UUID) -> RatingResponse:
        """Get a rating by its ID."""
        logger.info(f"Fetching rating with ID {rating_id}")
        rating = self.repository.get_rating_by_id(rating_id)
        if not rating:
            logger.warning(f"Rating not found with ID {rating_id}")
            raise NotFoundException(
                message="Rating not found",
                details={"rating_id": str(rating_id)}
            )
        logger.info(f"Rating found with ID {rating_id}")
        return RatingResponse(**rating)

    def list_ratings_by_professional(self, professional_id: UUID, page: int = 1, size: int = 10) -> tuple[List[RatingResponse], int]:
        """List ratings for a professional."""
        try:
            logger.info(f"Listing ratings for professional {professional_id} (page {page}, size {size})")
            ratings, total = self.repository.list_ratings_by_professional(professional_id, page, size)
            logger.info(f"Found {len(ratings)} ratings for professional {professional_id} (total: {total})")
            return [RatingResponse(**r) for r in ratings], total
        except Exception as e:
            logger.error(f"Error listing ratings: {str(e)}")
            raise DatabaseException(
                message="Failed to list ratings",
                details={"error": str(e)}
            )

    def delete_rating(self, rating_id: UUID) -> None:
        """Delete a rating by its ID."""
        try:
            logger.info(f"Deleting rating {rating_id}")
            deleted = self.repository.delete_rating(rating_id)
            if not deleted:
                logger.warning(f"Rating not found with ID {rating_id}")
                raise NotFoundException(
                    message="Rating not found",
                    details={"rating_id": str(rating_id)}
                )
            logger.info(f"Rating {rating_id} deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting rating: {str(e)}")
            raise DatabaseException(
                message="Failed to delete rating",
                details={"error": str(e)}
            )

    def list_ratings_by_consumer(self, consumer_id: UUID, page: int = 1, size: int = 10) -> tuple[List[RatingResponse], int]:
        """List ratings made by a consumer."""
        try:
            logger.info(f"Listing ratings made by consumer {consumer_id} (page {page}, size {size})")
            ratings, total = self.repository.list_ratings_by_consumer(consumer_id, page, size)
            logger.info(f"Found {len(ratings)} ratings made by consumer {consumer_id} (total: {total})")
            return [RatingResponse(**r) for r in ratings], total
        except Exception as e:
            logger.error(f"Error listing ratings: {str(e)}")
            raise DatabaseException(
                message="Failed to list ratings",
                details={"error": str(e)}
            )

def get_rating_service(repo: RatingRepository = Depends(get_rating_repository)) -> RatingService:
    return RatingService(repo) 