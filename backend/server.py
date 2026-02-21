from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path
import logging
import time
import traceback

from config import CORS_ORIGINS, DB_NAME, ENVIRONMENT, RATE_LIMIT_ENABLED, LOG_LEVEL
from database import db, client
from helpers import utcnow
from hotel_data import ROOMS

# Import all routers
from routers.hotel import router as hotel_router
from routers.auth import router as auth_router, verify_token
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

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv(Path(__file__).parent / '.env')

app = FastAPI(
    title="Kozbeyli Konagi API",
    description="Kozbeyli Konagi Hotel Management System API",
    version="2.0.0",
    docs_url="/api/docs" if ENVIRONMENT != "production" else None,
    redoc_url="/api/redoc" if ENVIRONMENT != "production" else None,
)
api = APIRouter(prefix="/api")


# ==================== MIDDLEWARE ====================

# --- Global Error Handler ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch unhandled exceptions and return proper JSON response"""
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {exc}")
    if ENVIRONMENT == "development":
        logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Sunucu hatasi olustu",
            "error": str(exc) if ENVIRONMENT == "development" else "Internal server error",
        }
    )


# --- Request Logging Middleware ---
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Log all requests with timing information"""
    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)

    # Only log slow requests or errors in production
    if ENVIRONMENT == "production":
        if duration_ms > 1000 or response.status_code >= 400:
            logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)")
    else:
        logger.debug(f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)")

    response.headers["X-Response-Time"] = f"{duration_ms}ms"
    return response


# --- Rate Limiting Middleware ---
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting to all API endpoints"""
    if not RATE_LIMIT_ENABLED:
        return await call_next(request)

    path = request.url.path
    if path in ("/api/health", "/health") or not path.startswith("/api/"):
        return await call_next(request)

    from rate_limiter import check_rate_limit, get_client_identifier
    identifier = get_client_identifier(request)

    if "/auth/login" in path:
        endpoint_type = "login"
    elif "/chatbot" in path:
        endpoint_type = "chatbot"
    elif "/reviews" in path:
        endpoint_type = "reviews"
    else:
        endpoint_type = "default"

    result = check_rate_limit(identifier, endpoint_type)
    if not result["allowed"]:
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Cok fazla istek gonderdiniz. Lutfen biraz bekleyin.",
                "retry_after": result["retry_after"],
            },
            headers={"Retry-After": str(result["retry_after"])}
        )

    return await call_next(request)


# --- Auth Middleware ---
PUBLIC_PATHS = [
    "/api/health",
    "/api/auth/login",
    "/api/auth/setup",
    "/api/auth/refresh",
    "/api/auth/roles",
    "/api/webhooks/",
    "/api/whatsapp/webhook",
    "/api/public/",
    "/api/public-menu",
    "/api/hotel/info",
    "/api/hotel/guide",
    "/api/hotel/awards",
    "/api/hotel/policies",
    "/api/hotel/history",
    "/api/i18n",
    "/api/seed",
    "/api/hotelrunner/webhook",
    "/api/docs",
    "/api/redoc",
    "/api/openapi.json",
    "/api/kvkk",
    "/api/notifications/vapid-key",
]


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """Require authentication for all API endpoints except public ones"""
    path = request.url.path

    if not path.startswith("/api/"):
        return await call_next(request)

    for public_path in PUBLIC_PATHS:
        if path.startswith(public_path):
            return await call_next(request)

    if request.method == "OPTIONS":
        return await call_next(request)

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"detail": "Yetkilendirme gerekli — Authorization header eksik"}
        )

    try:
        token = auth_header.split(" ")[1]
        verify_token(token)
    except Exception:
        return JSONResponse(
            status_code=401,
            content={"detail": "Gecersiz veya suresi dolmus token — tekrar giris yapin"}
        )

    return await call_next(request)


# ==================== HEALTH ====================

@api.get("/health")
async def health():
    """Comprehensive health check"""
    checks = {"api": "ok"}

    try:
        await db.command("ping")
        checks["database"] = "connected"
    except Exception as e:
        checks["database"] = f"error: {str(e)}"

    try:
        rooms_count = await db.rooms.count_documents({})
        users_count = await db.users.count_documents({})
        checks["rooms"] = rooms_count
        checks["users"] = users_count
        checks["seeded"] = rooms_count > 0
    except Exception:
        pass

    all_healthy = checks.get("database") == "connected"

    return {
        "status": "healthy" if all_healthy else "degraded",
        "hotel": "Kozbeyli Konagi",
        "environment": ENVIRONMENT,
        "checks": checks,
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

app.include_router(api)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=CORS_ORIGINS if CORS_ORIGINS != ['*'] else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Response-Time"],
)


@app.on_event("startup")
async def startup():
    logger.info(f"Kozbeyli Konagi API starting — env={ENVIRONMENT}, db={DB_NAME}")

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

    logger.info("Kozbeyli Konagi API ready")


@app.on_event("shutdown")
async def shutdown():
    logger.info("Kozbeyli Konagi API shutting down")
    client.close()
