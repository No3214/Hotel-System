from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path
import logging

from config import CORS_ORIGINS, DB_NAME
from database import db, client
from helpers import utcnow
from hotel_data import ROOMS

# Import all routers
from routers.hotel import router as hotel_router
from routers.auth import router as auth_router
from routers.rooms import router as rooms_router
from routers.guests import router as guests_router
from routers.reservations import router as reservations_router
from routers.tasks import router as tasks_router
from routers.events import router as events_router
from routers.housekeeping import router as housekeeping_router
from routers.staff import router as staff_router
from routers.knowledge import router as knowledge_router
from routers.chatbot import router as chatbot_router
from routers.messages import router as messages_router
from routers.campaigns import router as campaigns_router
from routers.reviews import router as reviews_router
from routers.settings import router as settings_router
from routers.pricing import router as pricing_router
from routers.table_reservations import router as table_router
from routers.lifecycle import router as lifecycle_router

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv(Path(__file__).parent / '.env')

app = FastAPI(title="Kozbeyli Konagi API")
api = APIRouter(prefix="/api")


# ==================== HEALTH ====================

@api.get("/health")
async def health():
    try:
        await db.command("ping")
        return {"status": "healthy", "database": "connected", "hotel": "Kozbeyli Konagi"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# ==================== SEED ====================

@api.post("/seed")
async def seed_database():
    from hotel_data import HOTEL_POLICIES
    from helpers import new_id

    rooms_count = await db.rooms.count_documents({})
    if rooms_count == 0:
        for room in ROOMS:
            await db.rooms.insert_one({**room, "created_at": utcnow()})

    knowledge_count = await db.knowledge.count_documents({})
    if knowledge_count == 0:
        knowledge_items = [
            {"id": new_id(), "title": "Iptal Politikasi", "content": HOTEL_POLICIES["cancellation"]["tr"], "category": "policy", "tags": ["iptal", "ceza"], "created_at": utcnow(), "updated_at": utcnow()},
            {"id": new_id(), "title": "No-Show Politikasi", "content": HOTEL_POLICIES["no_show"]["tr"], "category": "policy", "tags": ["no-show", "ceza"], "created_at": utcnow(), "updated_at": utcnow()},
            {"id": new_id(), "title": "On Odeme Kurali", "content": HOTEL_POLICIES["saturday_payment"]["tr"], "category": "policy", "tags": ["odeme", "cumartesi"], "created_at": utcnow(), "updated_at": utcnow()},
            {"id": new_id(), "title": "Kahvalti Bilgisi", "content": HOTEL_POLICIES["breakfast"], "category": "service", "tags": ["kahvalti", "organik"], "created_at": utcnow(), "updated_at": utcnow()},
            {"id": new_id(), "title": "Evcil Hayvan Politikasi", "content": HOTEL_POLICIES["pets"], "category": "policy", "tags": ["hayvan", "pet"], "created_at": utcnow(), "updated_at": utcnow()},
            {"id": new_id(), "title": "Cocuk Politikasi", "content": HOTEL_POLICIES["children"], "category": "policy", "tags": ["cocuk", "bebek"], "created_at": utcnow(), "updated_at": utcnow()},
        ]
        for item in knowledge_items:
            await db.knowledge.insert_one(item)

    return {"success": True, "message": "Veri tabanina baslangic verileri yuklendi."}


# ==================== INCLUDE ROUTERS ====================

api.include_router(hotel_router)
api.include_router(auth_router)
api.include_router(rooms_router)
api.include_router(guests_router)
api.include_router(reservations_router)
api.include_router(tasks_router)
api.include_router(events_router)
api.include_router(housekeeping_router)
api.include_router(staff_router)
api.include_router(knowledge_router)
api.include_router(chatbot_router)
api.include_router(messages_router)
api.include_router(campaigns_router)
api.include_router(reviews_router)
api.include_router(settings_router)
api.include_router(pricing_router)
api.include_router(table_router)
api.include_router(lifecycle_router)

app.include_router(api)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=CORS_ORIGINS if CORS_ORIGINS != ['*'] else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    logger.info(f"Kozbeyli Konagi API starting - DB: {DB_NAME}")
    rooms_count = await db.rooms.count_documents({})
    if rooms_count == 0:
        for room in ROOMS:
            await db.rooms.insert_one({**room, "created_at": utcnow()})
        logger.info("Rooms seeded successfully")


@app.on_event("shutdown")
async def shutdown():
    client.close()
