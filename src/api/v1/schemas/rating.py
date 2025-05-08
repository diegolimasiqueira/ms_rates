from pydantic import BaseModel, Field, UUID4, conint
from typing import Optional, List
from datetime import datetime

class RatingCreate(BaseModel):
    """Schema for creating a new rating."""
    professional_id: UUID4 = Field(
        ...,
        description="ID of the professional being rated",
        example="123e4567-e89b-12d3-a456-426614174001"
    )
    consumer_id: UUID4 = Field(
        ...,
        description="ID of the consumer making the rating",
        example="123e4567-e89b-12d3-a456-426614174002"
    )
    rate: conint(ge=0, le=5) = Field(
        ...,
        description="Rating value (0 to 5)",
        example=5
    )
    description: Optional[str] = Field(
        None,
        description="Optional rating description",
        example="Excellent service!"
    )

    class Config:
        schema_extra = {
            "example": {
                "professional_id": "123e4567-e89b-12d3-a456-426614174001",
                "consumer_id": "123e4567-e89b-12d3-a456-426614174002",
                "rate": 5,
                "description": "Excellent service!"
            }
        }

class RatingResponse(BaseModel):
    """Schema for rating response."""
    id: UUID4 = Field(
        ...,
        alias="_id",
        description="Unique rating ID",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    professional_id: UUID4 = Field(
        ...,
        description="ID of the rated professional",
        example="123e4567-e89b-12d3-a456-426614174001"
    )
    consumer_id: UUID4 = Field(
        ...,
        description="ID of the consumer who made the rating",
        example="123e4567-e89b-12d3-a456-426614174002"
    )
    rate: int = Field(
        ...,
        description="Rating value (0 to 5)",
        example=5
    )
    description: Optional[str] = Field(
        None,
        description="Rating description",
        example="Excellent service!"
    )
    created_at: datetime = Field(
        ...,
        description="Rating creation date and time",
        example="2024-03-20T10:00:00Z"
    )

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "123e4567-e89b-12d3-a456-426614174000",
                "professional_id": "123e4567-e89b-12d3-a456-426614174001",
                "consumer_id": "123e4567-e89b-12d3-a456-426614174002",
                "rate": 5,
                "description": "Excellent service!",
                "created_at": "2024-03-20T10:00:00Z"
            }
        }

class PaginatedResponse(BaseModel):
    """Schema for paginated rating response."""
    items: List[RatingResponse] = Field(
        ...,
        description="List of ratings"
    )
    total: int = Field(
        ...,
        description="Total number of ratings found",
        example=1
    )
    page: int = Field(
        ...,
        description="Current page number",
        example=1
    )
    size: int = Field(
        ...,
        description="Page size",
        example=10
    )
    pages: int = Field(
        ...,
        description="Total number of pages",
        example=1
    )

    class Config:
        schema_extra = {
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