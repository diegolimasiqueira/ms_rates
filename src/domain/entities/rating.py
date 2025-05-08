from uuid import UUID
from typing import Optional
from datetime import datetime

class Rating:
    """Domain entity for a professional rating."""
    def __init__(
        self,
        _id: UUID,
        professional_id: UUID,
        consumer_id: UUID,
        rate: int,
        description: Optional[str],
        created_at: datetime
    ):
        self._id = _id
        self.professional_id = professional_id
        self.consumer_id = consumer_id
        self.rate = rate
        self.description = description
        self.created_at = created_at 