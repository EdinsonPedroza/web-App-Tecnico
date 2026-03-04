import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from config import redact_mongo_url

logger = logging.getLogger(__name__)

mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
logger.info(f"Connecting to MongoDB at: {redact_mongo_url(mongo_url)}")

try:
    client = AsyncIOMotorClient(
        mongo_url,
        maxPoolSize=50,
        minPoolSize=5,
        maxIdleTimeMS=30000,
        connectTimeoutMS=5000,
        serverSelectionTimeoutMS=5000,
    )
    db = client[os.environ.get('DB_NAME', 'WebApp')]
    logger.info(f"MongoDB client initialized for database: {os.environ.get('DB_NAME', 'WebApp')}")
except Exception as e:
    logger.error(f"Failed to initialize MongoDB client: {e}")
    raise
