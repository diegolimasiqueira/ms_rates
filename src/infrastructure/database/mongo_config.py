import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class MongoConfig:
    """Centralizes access to MongoDB connection string."""
    @staticmethod
    def get_uri() -> str:
        load_dotenv()
        uri = os.getenv("MONGODB_URI")
        if not uri:
            raise RuntimeError("MONGODB_URI is not set in environment variables.")
        logger.info(f"MongoDB URI: {uri}")
        return uri 