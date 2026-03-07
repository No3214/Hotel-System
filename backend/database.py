import logging
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URL, DB_NAME

logger = logging.getLogger(__name__)

if not MONGO_URL:
    raise ValueError("MONGO_URL environment variable is required")
if not DB_NAME:
    raise ValueError("DB_NAME environment variable is required")

client = AsyncIOMotorClient(MONGO_URL, maxPoolSize=50, minPoolSize=5)
db = client[DB_NAME]


async def verify_connection():
    """Verify MongoDB connection is working."""
    try:
        await client.admin.command('ping')
        logger.info(f"MongoDB connected: {DB_NAME}")
        return True
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        return False
