from abc import ABC, abstractmethod
from uuid import UUID
from typing import List, Optional, Dict, Any

class RatingRepository(ABC):
    """Repository interface for ratings."""

    @abstractmethod
    def create_rating(self, rating: Dict[str, Any]) -> None:
        """Create a new rating in the database."""
        pass

    @abstractmethod
    def get_rating_by_id(self, rating_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a rating by its ID."""
        pass

    @abstractmethod
    def list_ratings_by_professional(self, professional_id: UUID) -> List[Dict[str, Any]]:
        """List ratings for a professional, ordered by created_at descending."""
        pass 