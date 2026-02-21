import os

# Use mongomock if real MongoDB is not available
USE_MONGOMOCK = os.environ.get('USE_MONGOMOCK', 'false').lower() == 'true'

if USE_MONGOMOCK:
    from mongomock_motor import AsyncMongoMockClient as AsyncIOMotorClient
else:
    from motor.motor_asyncio import AsyncIOMotorClient

from config import MONGO_URL, DB_NAME

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
