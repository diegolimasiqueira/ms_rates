import logging
from fastapi import APIRouter, Depends, Query
from uuid import UUID
from typing import List
from src.api.v1.schemas.rating import RatingCreate, RatingResponse, PaginatedResponse
from src.application.services.rating_service import RatingService, get_rating_service
from src.domain.exceptions.base_exceptions import ValidationException, NotFoundException, DatabaseException

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=RatingResponse, status_code=201)
def create_rating(rating: RatingCreate, service: RatingService = Depends(get_rating_service)):
    """Create a new rating."""
    try:
        logger.info(f"Received request to create rating for professional {rating.professional_id}")
        return service.create_rating(rating)
    except ValidationException as e:
        logger.error(f"Invalid rating data: {str(e)}")
        raise e
    except DatabaseException as e:
        logger.error(f"Database error creating rating: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error creating rating: {str(e)}")
        raise DatabaseException(details={"error": str(e)})

@router.get("/{id}", response_model=RatingResponse)
def get_rating(id: UUID, service: RatingService = Depends(get_rating_service)):
    """Get a rating by its ID."""
    try:
        logger.info(f"Received request to get rating {id}")
        return service.get_rating_by_id(id)
    except NotFoundException as e:
        logger.warning(f"Rating not found: {str(e)}")
        raise e
    except ValidationException as e:
        logger.error(f"Invalid rating data: {str(e)}")
        raise e
    except DatabaseException as e:
        logger.error(f"Database error getting rating: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error getting rating: {str(e)}")
        raise DatabaseException(details={"error": str(e)})

@router.get("/professional/{professional_id}", response_model=PaginatedResponse)
def list_ratings_by_professional(
    professional_id: UUID,
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(10, ge=1, le=100, description="Tamanho da página"),
    service: RatingService = Depends(get_rating_service)
):
    """List ratings for a professional."""
    try:
        logger.info(f"Received request to list ratings for professional {professional_id} (page {page}, size {size})")
        ratings, total = service.list_ratings_by_professional(professional_id, page, size)
        pages = (total + size - 1) // size  # Arredonda para cima
        return PaginatedResponse(
            items=ratings,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    except ValidationException as e:
        logger.error(f"Invalid rating data: {str(e)}")
        raise e
    except DatabaseException as e:
        logger.error(f"Database error listing ratings: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error listing ratings: {str(e)}")
        raise DatabaseException(details={"error": str(e)})

@router.delete("/{id}", status_code=204)
def delete_rating(id: UUID, service: RatingService = Depends(get_rating_service)):
    """Delete a rating by its ID."""
    try:
        logger.info(f"Received request to delete rating {id}")
        service.delete_rating(id)
    except NotFoundException as e:
        logger.warning(f"Rating not found: {str(e)}")
        raise e
    except ValidationException as e:
        logger.error(f"Invalid rating data: {str(e)}")
        raise e
    except DatabaseException as e:
        logger.error(f"Database error deleting rating: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error deleting rating: {str(e)}")
        raise DatabaseException(details={"error": str(e)}) 