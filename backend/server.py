from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
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
from routers.table_reservations import router as table_router
from routers.lifecycle import router as lifecycle_router
from routers.automation import router as automation_router
from routers.public_menu import router as public_menu_router
from routers.menu_admin import router as menu_admin_router
from routers.social_media import router as social_media_router
from routers.whatsapp import router as whatsapp_router
from routers.loyalty import router as loyalty_router
from routers.analytics import router as analytics_router
from routers.audit import router as audit_router
from routers.hotelrunner import router as hotelrunner_router
from routers.cache import router as cache_router
from routers.notifications import router as notifications_router
from routers.qr import router as qr_router
from routers.webhooks import router as webhooks_router
from routers.organization import router as organization_router
from routers.proposals import router as proposals_router
from routers.event_leads import router as event_leads_router
from routers.escalation import router as escalation_router
from routers.marketing import router as marketing_router
from routers.meta_ads import router as meta_ads_router
from routers.reputation import router as reputation_router
from routers.marketing_analytics import router as marketing_analytics_router
from routers.google_ads import router as google_ads_router
from routers.ai_providers import router as ai_providers_router
from routers.presence import router as presence_router
from routers.financials import router as financials_router
from routers.kitchen import router as kitchen_router
from routers.pricing import router as pricing_router
from routers.revenue import router as revenue_router
from routers.seo import router as seo_router
from routers.competitor import router as competitor_router

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv(Path(__file__).parent / '.env')

app = FastAPI(title="Kozbeyli Konagi API")
api = APIRouter(prefix="/api")


# ==================== GLOBAL ERROR HANDLER ====================
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions and return proper JSON error."""
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Sunucu hatasi olustu. Lutfen tekrar deneyin.",
            "error_type": type(exc).__name__,
        },
    )


# ==================== HEALTH ====================

@api.get("/health")
async def health():
    try:
        await db.command("ping")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    # Redis check
    try:
        from services.cache_service import _get_redis
        r = _get_redis()
        if r:
            r.ping()
            redis_status = "connected"
        else:
            redis_status = "fallback_memory"
    except Exception as e:
        redis_status = f"error: {str(e)}"

    # Celery worker check
    try:
        from celery_app import celery_app as _celery
        inspect = _celery.control.inspect(timeout=2.0)
        active = inspect.ping()
        celery_status = "connected" if active else "no_workers"
    except Exception as e:
        celery_status = f"unreachable: {str(e)}"

    # Collect system info
    import os
    checks = {
        "database": db_status,
        "redis": redis_status,
        "celery": celery_status,
        "google_api_key": "configured" if os.environ.get("GOOGLE_API_KEY") else "missing",
        "meta_token": "configured" if os.environ.get("META_ACCESS_TOKEN") else "not_set",
        "vapid_key": "configured" if os.environ.get("VAPID_PUBLIC_KEY") else "not_set",
        "celery_broker": "configured" if os.environ.get("CELERY_BROKER_URL") else "using_default",
    }

    # Count collections (parallel)
    try:
        import asyncio
        rooms_c, res_c, guests_c, social_c, tasks_c = await asyncio.gather(
            db.rooms.count_documents({}),
            db.reservations.count_documents({}),
            db.guests.count_documents({}),
            db.social_posts.count_documents({}),
            db.tasks.count_documents({}),
        )
        collections_stats = {
            "rooms": rooms_c, "reservations": res_c, "guests": guests_c,
            "social_posts": social_c, "tasks": tasks_c,
        }
    except Exception:
        collections_stats = {}

    is_healthy = db_status == "connected"
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "hotel": "Kozbeyli Konagi",
        "checks": checks,
        "collections": collections_stats,
    }


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
api.include_router(table_router)
api.include_router(lifecycle_router)
api.include_router(automation_router)
api.include_router(public_menu_router)
api.include_router(menu_admin_router)
api.include_router(social_media_router)
api.include_router(whatsapp_router)
api.include_router(loyalty_router)
api.include_router(analytics_router)
api.include_router(audit_router)
api.include_router(hotelrunner_router)
api.include_router(cache_router)
api.include_router(notifications_router)
api.include_router(qr_router)
api.include_router(webhooks_router)
api.include_router(organization_router)
api.include_router(proposals_router)
api.include_router(event_leads_router)
api.include_router(escalation_router)
api.include_router(marketing_router)
api.include_router(meta_ads_router)
api.include_router(reputation_router)
api.include_router(marketing_analytics_router)
api.include_router(google_ads_router)
api.include_router(ai_providers_router)
api.include_router(presence_router)
api.include_router(financials_router)
api.include_router(kitchen_router)
api.include_router(pricing_router)
api.include_router(revenue_router)
api.include_router(seo_router)
api.include_router(competitor_router)

app.include_router(api)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=CORS_ORIGINS if CORS_ORIGINS != ['*'] else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== FRONTEND STATIC FILES ====================

FRONTEND_DIR = Path(__file__).parent / "static_frontend"

if FRONTEND_DIR.exists() and (FRONTEND_DIR / "index.html").exists():
    # Serve static assets (JS, CSS, images) from /static subdir
    static_dir = FRONTEND_DIR / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="frontend-static")

    # Serve other build assets (manifest, icons, etc.)
    @app.get("/manifest.json")
    async def manifest():
        return FileResponse(str(FRONTEND_DIR / "manifest.json"))

    @app.get("/favicon.ico")
    async def favicon():
        fav = FRONTEND_DIR / "favicon.ico"
        if fav.exists():
            return FileResponse(str(fav))
        return JSONResponse(status_code=404, content={"detail": "Not found"})

    # SPA catch-all: any non-API route serves index.html
    @app.get("/{path:path}")
    async def serve_spa(path: str):
        # Try to serve actual file first (e.g. logo, robots.txt)
        file_path = (FRONTEND_DIR / path).resolve()
        if path and file_path.is_relative_to(FRONTEND_DIR.resolve()) and file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        # Otherwise serve index.html for SPA routing
        return FileResponse(str(FRONTEND_DIR / "index.html"))
else:
    logger.warning("Frontend build not found at %s - serving API only", FRONTEND_DIR)


@app.on_event("startup")
async def startup():
    logger.info(f"Kozbeyli Konagi API starting - DB: {DB_NAME}")
    from database import verify_connection
    if not await verify_connection():
        logger.error("MongoDB connection failed - check MONGO_URL")
    rooms_count = await db.rooms.count_documents({})
    if rooms_count == 0:
        for room in ROOMS:
            await db.rooms.insert_one({**room, "created_at": utcnow()})
        logger.info("Rooms seeded successfully")

    # Database indexing
    from services.database_optimizer import apply_indexes
    await apply_indexes()

    # Celery beat baslat (background process)
    from celery_app import start_celery_beat
    start_celery_beat()
    logger.info("Celery beat started")


@app.on_event("shutdown")
async def shutdown():
    client.close()
    # Close httpx connection pool
    from services.ai_provider_service import close_http_client
    await close_http_client()
