import logging
from src.domain.interfaces.rating_repository import RatingRepository
from src.infrastructure.database.mongo_client import get_ratings_collection
from src.domain.exceptions.base_exceptions import ValidationException, DatabaseException
from uuid import UUID
from typing import List, Optional, Dict, Any
from fastapi import Depends
import bson
from pymongo.errors import WriteError, OperationFailure
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class RatingRepositoryImpl(RatingRepository):
    """MongoDB implementation of RatingRepository."""
    def __init__(self):
        self.collection = get_ratings_collection()

    def create_rating(self, rating: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new rating."""
        try:
            doc = rating.copy()
            # Gera um novo UUID para o _id
            doc["_id"] = str(uuid.uuid4())
            # Converte os UUIDs para string
            doc["professional_id"] = str(doc["professional_id"])
            doc["consumer_id"] = str(doc["consumer_id"])
            # Adiciona o timestamp atual
            doc["created_at"] = datetime.utcnow()
            logger.info(f"Tentando inserir documento: {doc}")
            self.collection.insert_one(doc)
            return doc
        except WriteError as e:
            logger.error(f"MongoDB validation error: {str(e)}")
            raise ValidationException(
                message="Invalid rating data",
                details={"error": str(e)}
            )
        except OperationFailure as e:
            logger.error(f"MongoDB operation error: {str(e)}")
            raise DatabaseException(
                message="Database operation failed",
                details={"error": str(e)}
            )
        except Exception as e:
            logger.error(f"Unexpected error creating rating: {str(e)}")
            logger.exception("Stack trace:")
            raise DatabaseException(
                message="Failed to create rating",
                details={"error": str(e)}
            )

    def get_rating_by_id(self, rating_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a rating by its ID."""
        try:
            doc = self.collection.find_one({"_id": str(rating_id)})
            if doc:
                return self._doc_to_dict(doc)
            return None
        except Exception as e:
            logger.error(f"Error fetching rating {rating_id}: {str(e)}")
            raise DatabaseException(
                message="Failed to fetch rating",
                details={"error": str(e)}
            )

    def list_ratings_by_professional(self, professional_id: UUID, page: int = 1, size: int = 10) -> tuple[List[Dict[str, Any]], int]:
        """List ratings for a professional."""
        try:
            # Calcula o total de documentos
            total = self.collection.count_documents({"professional_id": str(professional_id)})
            
            # Calcula o skip baseado na página e tamanho
            skip = (page - 1) * size
            
            # Busca os documentos paginados
            cursor = self.collection.find(
                {"professional_id": str(professional_id)}
            ).sort("created_at", -1).skip(skip).limit(size)
            
            return [self._doc_to_dict(doc) for doc in cursor], total
        except Exception as e:
            logger.error(f"Error listing ratings for professional {professional_id}: {str(e)}")
            raise DatabaseException(
                message="Failed to list ratings",
                details={"error": str(e)}
            )

    def _doc_to_dict(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MongoDB document to dictionary."""
        return {
            "_id": UUID(doc["_id"]),
            "professional_id": UUID(doc["professional_id"]),
            "consumer_id": UUID(doc["consumer_id"]),
            "rate": doc["rate"],
            "description": doc.get("description"),
            "created_at": doc["created_at"]
        }

    def delete_rating(self, rating_id: UUID) -> bool:
        """Delete a rating by its ID."""
        try:
            result = self.collection.delete_one({"_id": str(rating_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting rating {rating_id}: {str(e)}")
            raise DatabaseException(
                message="Failed to delete rating",
                details={"error": str(e)}
            )

def get_rating_repository() -> RatingRepository:
    return RatingRepositoryImpl() 