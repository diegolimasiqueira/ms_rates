from pydantic import BaseModel, Field, UUID4, conint
from typing import Optional, List
from datetime import datetime

class RatingCreate(BaseModel):
    professional_id: UUID4
    consumer_id: UUID4
    rate: conint(ge=0, le=5)
    description: Optional[str] = None

class RatingResponse(BaseModel):
    id: UUID4 = Field(alias="_id")
    professional_id: UUID4
    consumer_id: UUID4
    rate: int
    description: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

class PaginatedResponse(BaseModel):
    items: List[RatingResponse]
    total: int
    page: int
    size: int
    pages: int 