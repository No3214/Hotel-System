import os
import logging

logger = logging.getLogger(__name__)

# Use mongomock if real MongoDB is not available
USE_MONGOMOCK = os.environ.get('USE_MONGOMOCK', 'false').lower() == 'true'

if USE_MONGOMOCK:
    from mongomock_motor import AsyncMongoMockClient as AsyncIOMotorClient
else:
    from motor.motor_asyncio import AsyncIOMotorClient

from config import MONGO_URL, DB_NAME

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]


# ==================== SCHEMA VALIDATION ====================

COLLECTION_VALIDATORS = {
    "reservations": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["id", "guest_name", "check_in", "check_out", "status"],
            "properties": {
                "id": {"bsonType": "string"},
                "guest_name": {"bsonType": "string", "minLength": 1},
                "check_in": {"bsonType": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"},
                "check_out": {"bsonType": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"},
                "status": {
                    "bsonType": "string",
                    "enum": ["pending", "confirmed", "checked_in", "checked_out", "cancelled", "no_show"],
                },
                "total_price": {"bsonType": ["double", "int", "long", "decimal"]},
                "room_id": {"bsonType": "string"},
            },
        }
    },
    "guests": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["id", "name"],
            "properties": {
                "id": {"bsonType": "string"},
                "name": {"bsonType": "string", "minLength": 1},
                "email": {"bsonType": ["string", "null"]},
                "phone": {"bsonType": ["string", "null"]},
            },
        }
    },
    "rooms": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["room_id"],
            "properties": {
                "room_id": {"bsonType": ["string", "int"]},
                "type": {"bsonType": "string"},
                "status": {
                    "bsonType": "string",
                    "enum": ["available", "occupied", "maintenance", "cleaning"],
                },
            },
        }
    },
    "users": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["id", "username", "password_hash", "role"],
            "properties": {
                "id": {"bsonType": "string"},
                "username": {"bsonType": "string", "minLength": 3},
                "password_hash": {"bsonType": "string"},
                "role": {
                    "bsonType": "string",
                    "enum": ["admin", "manager", "receptionist", "staff", "viewer"],
                },
            },
        }
    },
    "financials": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["id", "type", "amount"],
            "properties": {
                "id": {"bsonType": "string"},
                "type": {"bsonType": "string", "enum": ["income", "expense"]},
                "amount": {"bsonType": ["double", "int", "long", "decimal"]},
                "category": {"bsonType": "string"},
            },
        }
    },
}


async def apply_schema_validation():
    """Apply MongoDB schema validators to critical collections."""
    existing = await db.list_collection_names()
    for collection_name, validator in COLLECTION_VALIDATORS.items():
        try:
            if collection_name in existing:
                await db.command("collMod", collection_name, validator=validator, validationLevel="moderate")
            else:
                await db.create_collection(collection_name, validator=validator)
            logger.info(f"Schema validation applied: {collection_name}")
        except Exception as e:
            logger.warning(f"Schema validation skipped for {collection_name}: {e}")
