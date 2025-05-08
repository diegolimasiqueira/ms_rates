from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import CollectionInvalid
from src.infrastructure.database.mongo_config import MongoConfig
import uuid
import logging

logger = logging.getLogger(__name__)

RATINGS_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["_id", "professional_id", "consumer_id", "rate", "created_at"],
        "properties": {
            "_id": {"bsonType": "string", "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"},
            "professional_id": {"bsonType": "string", "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"},
            "consumer_id": {"bsonType": "string", "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"},
            "rate": {"bsonType": "int", "minimum": 0, "maximum": 5},
            "description": {"bsonType": ["string", "null"]},
            "created_at": {"bsonType": "date"}
        }
    }
}

_mongo_client = None

def get_mongo_client():
    global _mongo_client
    if _mongo_client is None:
        uri = MongoConfig.get_uri()
        logger.info(f"Connecting to MongoDB with URI: {uri}")
        _mongo_client = MongoClient(uri, port=27017)
    return _mongo_client

def set_mongo_client(client):
    global _mongo_client
    _mongo_client = client

def get_ratings_collection():
    client = get_mongo_client()
    db = client["easyprofind"]
    coll_name = "ratings"
    if coll_name not in db.list_collection_names():
        try:
            if isinstance(client, MongoClient):
                db.create_collection(
                    coll_name,
                    validator=RATINGS_VALIDATOR
                )
            else:
                # mongomock não suporta validação
                db.create_collection(coll_name)
        except CollectionInvalid:
            pass
    # Ensure indexes
    coll = db[coll_name]
    coll.create_index([("professional_id", ASCENDING)])
    coll.create_index([("consumer_id", ASCENDING)])
    coll.create_index([("professional_id", DESCENDING), ("created_at", DESCENDING)])
    return coll 