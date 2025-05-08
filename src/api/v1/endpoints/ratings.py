import logging
from fastapi import APIRouter, Depends, Query, status, HTTPException
from uuid import UUID
from typing import List
from src.api.v1.schemas.rating import RatingCreate, RatingResponse, PaginatedResponse
from src.application.services.rating_service import RatingService, get_rating_service
from src.domain.exceptions.base_exceptions import ValidationException, NotFoundException, DatabaseException
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/ratings",
    tags=["Ratings"],
    responses={
        400: {"description": "Invalid input data"},
        404: {"description": "Resource not found"},
        500: {"description": "Internal server error"}
    }
)

@router.post(
    "/",
    response_model=RatingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new rating",
    description="""
    Create a new rating for a professional.
    
    - **professional_id**: ID of the professional being rated
    - **consumer_id**: ID of the consumer making the rating
    - **rate**: Rating value (0 to 5)
    - **description**: Optional rating description
    
    Returns the created rating data including the generated ID.
    """,
    responses={
        201: {
            "description": "Rating created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "_id": "123e4567-e89b-12d3-a456-426614174000",
                        "professional_id": "123e4567-e89b-12d3-a456-426614174001",
                        "consumer_id": "123e4567-e89b-12d3-a456-426614174002",
                        "rate": 5,
                        "description": "Excellent service!",
                        "created_at": "2024-03-20T10:00:00Z"
                    }
                }
            }
        }
    }
)
def create_rating(rating: RatingCreate, service: RatingService = Depends(get_rating_service)):
    """Create a new rating."""
    try:
        logger.info(f"Received request to create rating for professional {rating.professional_id}")
        return service.create_rating(rating)
    except PyMongoError as e:
        logger.error(f"MongoDB error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "An error occurred while accessing the database",
                "details": {"error": str(e)}
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "An unexpected error occurred",
                "details": {"error": str(e)}
            }
        )

@router.get(
    "/{id}",
    response_model=RatingResponse,
    summary="Get rating by ID",
    description="""
    Get a specific rating by its ID.
    
    - **id**: UUID of the rating to retrieve
    
    Returns the complete rating data if found.
    """,
    responses={
        200: {
            "description": "Rating found successfully",
            "content": {
                "application/json": {
                    "example": {
                        "_id": "123e4567-e89b-12d3-a456-426614174000",
                        "professional_id": "123e4567-e89b-12d3-a456-426614174001",
                        "consumer_id": "123e4567-e89b-12d3-a456-426614174002",
                        "rate": 5,
                        "description": "Excellent service!",
                        "created_at": "2024-03-20T10:00:00Z"
                    }
                }
            }
        },
        404: {
            "description": "Rating not found",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Rating not found",
                        "details": {"rating_id": "123e4567-e89b-12d3-a456-426614174000"}
                    }
                }
            }
        }
    }
)
def get_rating(id: UUID, service: RatingService = Depends(get_rating_service)):
    """Get a rating by its ID."""
    logger.info(f"Received request to get rating {id}")
    return service.get_rating_by_id(id)

@router.get(
    "/professional/{professional_id}",
    response_model=PaginatedResponse,
    summary="List ratings by professional",
    description="""
    List all ratings for a specific professional.
    
    - **professional_id**: ID of the professional
    - **page**: Page number (default: 1)
    - **size**: Page size (default: 10, max: 100)
    
    Returns a paginated list of ratings ordered by creation date (newest first).
    """,
    responses={
        200: {
            "description": "List of ratings returned successfully",
            "content": {
                "application/json": {
                    "example": {
                        "items": [
                            {
                                "_id": "123e4567-e89b-12d3-a456-426614174000",
                                "professional_id": "123e4567-e89b-12d3-a456-426614174001",
                                "consumer_id": "123e4567-e89b-12d3-a456-426614174002",
                                "rate": 5,
                                "description": "Excellent service!",
                                "created_at": "2024-03-20T10:00:00Z"
                            }
                        ],
                        "total": 1,
                        "page": 1,
                        "size": 10,
                        "pages": 1
                    }
                }
            }
        }
    }
)
def list_ratings_by_professional(
    professional_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    service: RatingService = Depends(get_rating_service)
):
    """List ratings for a professional."""
    logger.info(f"Received request to list ratings for professional {professional_id} (page {page}, size {size})")
    ratings, total = service.list_ratings_by_professional(professional_id, page, size)
    pages = (total + size - 1) // size  # Round up
    return PaginatedResponse(
        items=ratings,
        total=total,
        page=page,
        size=size,
        pages=pages
    )

@router.get(
    "/consumer/{consumer_id}",
    response_model=PaginatedResponse,
    summary="List ratings by consumer",
    description="""
    List all ratings made by a specific consumer.
    
    - **consumer_id**: ID of the consumer
    - **page**: Page number (default: 1)
    - **size**: Page size (default: 10, max: 100)
    
    Returns a paginated list of ratings ordered by creation date (newest first).
    """,
    responses={
        200: {
            "description": "List of ratings returned successfully",
            "content": {
                "application/json": {
                    "example": {
                        "items": [
                            {
                                "_id": "123e4567-e89b-12d3-a456-426614174000",
                                "professional_id": "123e4567-e89b-12d3-a456-426614174001",
                                "consumer_id": "123e4567-e89b-12d3-a456-426614174002",
                                "rate": 5,
                                "description": "Excellent service!",
                                "created_at": "2024-03-20T10:00:00Z"
                            }
                        ],
                        "total": 1,
                        "page": 1,
                        "size": 10,
                        "pages": 1
                    }
                }
            }
        }
    }
)
def list_ratings_by_consumer(
    consumer_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    service: RatingService = Depends(get_rating_service)
):
    """List ratings made by a consumer."""
    logger.info(f"Received request to list ratings made by consumer {consumer_id} (page {page}, size {size})")
    ratings, total = service.list_ratings_by_consumer(consumer_id, page, size)
    pages = (total + size - 1) // size  # Round up
    return PaginatedResponse(
        items=ratings,
        total=total,
        page=page,
        size=size,
        pages=pages
    )

@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a rating",
    description="""
    Delete a specific rating by its ID.
    
    - **id**: UUID of the rating to delete
    
    Returns 204 No Content on success.
    """,
    responses={
        204: {"description": "Rating deleted successfully"},
        404: {
            "description": "Rating not found",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Rating not found",
                        "details": {"rating_id": "123e4567-e89b-12d3-a456-426614174000"}
                    }
                }
            }
        }
    }
)
def delete_rating(id: UUID, service: RatingService = Depends(get_rating_service)):
    """Delete a rating by its ID."""
    logger.info(f"Received request to delete rating {id}")
    service.delete_rating(id) 