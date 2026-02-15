from fastapi import FastAPI, APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os
import logging
from datetime import datetime, timezone
from typing import Optional

from config import MONGO_URL, DB_NAME, CORS_ORIGINS
from models import (
    ChatRequest, TaskCreate, TaskUpdate, TaskStatus, TaskPriority,
    GuestCreate, ReservationCreate, ReservationUpdate, ReservationStatus, RoomStatus,
    EventCreate, HousekeepingCreate, HousekeepingStatus,
    KnowledgeCreate, StaffCreate, WhatsAppMessage,
    CampaignCreate, CampaignStatus, ShiftCreate,
)
from hotel_data import (
    HOTEL_INFO, ROOMS, RESTAURANT_MENU, HOTEL_AWARDS, HOTEL_RATINGS,
    HOTEL_POLICIES, HOTEL_HISTORY, FOCA_LOCAL_GUIDE, GEMINI_SYSTEM_PROMPT,
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv(Path(__file__).parent / '.env')

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

app = FastAPI(title="Kozbeyli Konagi API")
api = APIRouter(prefix="/api")


# ==================== HELPERS ====================

def utcnow():
    return datetime.now(timezone.utc).isoformat()


def new_id():
    import uuid
    return str(uuid.uuid4())


def clean_doc(doc):
    if doc and "_id" in doc:
        del doc["_id"]
    return doc


def clean_docs(docs):
    return [clean_doc(d) for d in docs]


# ==================== HEALTH ====================

@api.get("/health")
async def health():
    try:
        await db.command("ping")
        return {"status": "healthy", "database": "connected", "hotel": HOTEL_INFO["name"]}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# ==================== DASHBOARD ====================

@api.get("/dashboard/stats")
async def dashboard_stats():
    total_rooms = HOTEL_INFO["total_rooms"]
    occupied = await db.reservations.count_documents({"status": ReservationStatus.CHECKED_IN})
    total_guests = await db.guests.count_documents({})
    total_tasks = await db.tasks.count_documents({})
    pending_tasks = await db.tasks.count_documents({"status": TaskStatus.PENDING})
    total_reservations = await db.reservations.count_documents({})
    active_events = await db.events.count_documents({"is_active": True})
    housekeeping_pending = await db.housekeeping.count_documents({"status": HousekeepingStatus.PENDING})

    recent = await db.tasks.find({}, {"_id": 0}).sort("created_at", -1).limit(5).to_list(5)

    return {
        "total_rooms": total_rooms,
        "occupied_rooms": occupied,
        "available_rooms": total_rooms - occupied,
        "occupancy_rate": round((occupied / total_rooms) * 100, 1) if total_rooms else 0,
        "total_guests": total_guests,
        "total_tasks": total_tasks,
        "pending_tasks": pending_tasks,
        "total_reservations": total_reservations,
        "active_events": active_events,
        "housekeeping_pending": housekeeping_pending,
        "ratings": HOTEL_RATINGS,
        "recent_tasks": recent,
    }


# ==================== HOTEL INFO ====================

@api.get("/hotel/info")
async def get_hotel_info():
    return HOTEL_INFO


@api.get("/hotel/awards")
async def get_hotel_awards():
    return {"awards": HOTEL_AWARDS}


@api.get("/hotel/policies")
async def get_hotel_policies():
    return HOTEL_POLICIES


@api.get("/hotel/history")
async def get_hotel_history():
    return HOTEL_HISTORY


@api.get("/hotel/guide")
async def get_local_guide():
    return FOCA_LOCAL_GUIDE


# ==================== ROOMS ====================

@api.get("/rooms")
async def list_rooms():
    db_rooms = await db.rooms.find({}, {"_id": 0}).to_list(100)
    if not db_rooms:
        return {"rooms": ROOMS}
    return {"rooms": db_rooms}


@api.get("/rooms/{room_id}")
async def get_room(room_id: str):
    room = await db.rooms.find_one({"room_id": room_id}, {"_id": 0})
    if not room:
        for r in ROOMS:
            if r["room_id"] == room_id:
                return r
        raise HTTPException(404, "Oda bulunamadi")
    return room


# ==================== MENU ====================

@api.get("/menu")
async def get_menu():
    return {"menu": RESTAURANT_MENU, "restaurant": HOTEL_INFO["restaurant_name"]}


@api.get("/menu/{category}")
async def get_menu_category(category: str):
    if category not in RESTAURANT_MENU:
        raise HTTPException(404, f"Kategori bulunamadi: {category}")
    return {"category": category, "items": RESTAURANT_MENU[category]}


# ==================== GUESTS ====================

@api.get("/guests")
async def list_guests(search: Optional[str] = None, limit: int = 50, skip: int = 0):
    query = {}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"phone": {"$regex": search, "$options": "i"}},
        ]
    guests = await db.guests.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.guests.count_documents(query)
    return {"guests": guests, "total": total}


@api.post("/guests")
async def create_guest(data: GuestCreate):
    guest = {
        "id": new_id(),
        **data.model_dump(),
        "created_at": utcnow(),
        "updated_at": utcnow(),
        "total_stays": 0,
        "vip": False,
    }
    await db.guests.insert_one(guest)
    return clean_doc(guest)


@api.get("/guests/{guest_id}")
async def get_guest(guest_id: str):
    guest = await db.guests.find_one({"id": guest_id}, {"_id": 0})
    if not guest:
        raise HTTPException(404, "Misafir bulunamadi")
    return guest


@api.patch("/guests/{guest_id}")
async def update_guest(guest_id: str, data: dict):
    data["updated_at"] = utcnow()
    result = await db.guests.update_one({"id": guest_id}, {"$set": data})
    if result.matched_count == 0:
        raise HTTPException(404, "Misafir bulunamadi")
    return {"success": True}


# ==================== RESERVATIONS ====================

@api.get("/reservations")
async def list_reservations(status: Optional[str] = None, limit: int = 50, skip: int = 0):
    query = {}
    if status:
        query["status"] = status
    items = await db.reservations.find(query, {"_id": 0}).sort("check_in", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.reservations.count_documents(query)
    return {"reservations": items, "total": total}


@api.post("/reservations")
async def create_reservation(data: ReservationCreate):
    reservation = {
        "id": new_id(),
        **data.model_dump(),
        "status": ReservationStatus.PENDING,
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }
    await db.reservations.insert_one(reservation)
    return clean_doc(reservation)


@api.patch("/reservations/{res_id}/status")
async def update_reservation_status(res_id: str, status: str):
    update = {"status": status, "updated_at": utcnow()}
    if status == ReservationStatus.CHECKED_OUT:
        update["checked_out_at"] = utcnow()
    result = await db.reservations.update_one({"id": res_id}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(404, "Rezervasyon bulunamadi")
    return {"success": True}


# ==================== TASKS ====================

@api.get("/tasks")
async def list_tasks(status: Optional[str] = None, priority: Optional[str] = None, limit: int = 50, skip: int = 0):
    query = {}
    if status:
        query["status"] = status
    if priority:
        query["priority"] = priority
    tasks = await db.tasks.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.tasks.count_documents(query)
    return {"tasks": tasks, "total": total}


@api.post("/tasks")
async def create_task(data: TaskCreate):
    task = {
        "id": new_id(),
        **data.model_dump(),
        "status": TaskStatus.PENDING,
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }
    await db.tasks.insert_one(task)
    return clean_doc(task)


@api.patch("/tasks/{task_id}")
async def update_task(task_id: str, data: TaskUpdate):
    update = {k: v for k, v in data.model_dump().items() if v is not None}
    update["updated_at"] = utcnow()
    if data.status == TaskStatus.COMPLETED:
        update["completed_at"] = utcnow()
    result = await db.tasks.update_one({"id": task_id}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(404, "Gorev bulunamadi")
    return {"success": True}


@api.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    result = await db.tasks.delete_one({"id": task_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Gorev bulunamadi")
    return {"success": True}


# ==================== EVENTS ====================

@api.get("/events")
async def list_events(active_only: bool = False):
    query = {"is_active": True} if active_only else {}
    events = await db.events.find(query, {"_id": 0}).sort("event_date", 1).to_list(100)
    return {"events": events}


@api.post("/events")
async def create_event(data: EventCreate):
    event = {
        "id": new_id(),
        **data.model_dump(),
        "created_at": utcnow(),
        "updated_at": utcnow(),
        "registrations": 0,
    }
    await db.events.insert_one(event)
    return clean_doc(event)


@api.patch("/events/{event_id}")
async def update_event(event_id: str, data: dict):
    data["updated_at"] = utcnow()
    result = await db.events.update_one({"id": event_id}, {"$set": data})
    if result.matched_count == 0:
        raise HTTPException(404, "Etkinlik bulunamadi")
    return {"success": True}


@api.delete("/events/{event_id}")
async def delete_event(event_id: str):
    result = await db.events.delete_one({"id": event_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Etkinlik bulunamadi")
    return {"success": True}


# ==================== HOUSEKEEPING ====================

@api.get("/housekeeping")
async def list_housekeeping(status: Optional[str] = None):
    query = {"status": status} if status else {}
    logs = await db.housekeeping.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return {"logs": logs}


@api.post("/housekeeping")
async def create_housekeeping(data: HousekeepingCreate):
    log = {
        "id": new_id(),
        **data.model_dump(),
        "status": HousekeepingStatus.PENDING,
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }
    await db.housekeeping.insert_one(log)
    return clean_doc(log)


@api.patch("/housekeeping/{log_id}/status")
async def update_housekeeping(log_id: str, status: str):
    update = {"status": status, "updated_at": utcnow()}
    if status == HousekeepingStatus.COMPLETED:
        update["completed_at"] = utcnow()
    result = await db.housekeeping.update_one({"id": log_id}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(404, "Kayit bulunamadi")
    return {"success": True}


# ==================== STAFF ====================

@api.get("/staff")
async def list_staff():
    staff = await db.staff.find({}, {"_id": 0}).to_list(100)
    return {"staff": staff}


@api.post("/staff")
async def create_staff(data: StaffCreate):
    member = {
        "id": new_id(),
        **data.model_dump(),
        "created_at": utcnow(),
    }
    await db.staff.insert_one(member)
    return clean_doc(member)


# ==================== KNOWLEDGE BASE ====================

@api.get("/knowledge")
async def list_knowledge(category: Optional[str] = None, search: Optional[str] = None, limit: int = 50):
    query = {}
    if category:
        query["category"] = category
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"content": {"$regex": search, "$options": "i"}},
        ]
    items = await db.knowledge.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    total = await db.knowledge.count_documents(query)
    return {"items": items, "total": total}


@api.post("/knowledge")
async def create_knowledge(data: KnowledgeCreate):
    item = {
        "id": new_id(),
        **data.model_dump(),
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }
    await db.knowledge.insert_one(item)
    return clean_doc(item)


@api.delete("/knowledge/{item_id}")
async def delete_knowledge(item_id: str):
    result = await db.knowledge.delete_one({"id": item_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Bilgi bulunamadi")
    return {"success": True}


# ==================== AI CHATBOT ====================

@api.post("/chatbot")
async def chatbot(data: ChatRequest):
    from gemini_service import get_chat_response, detect_intent

    intent = detect_intent(data.message)
    context = ""

    if intent == "rooms":
        context = f"Oda bilgileri: {ROOMS}"
    elif intent == "menu":
        context = f"Menu: {RESTAURANT_MENU}"
    elif intent == "cancellation":
        context = f"Politikalar: {HOTEL_POLICIES}"
    elif intent == "local_guide":
        context = f"Cevre rehberi: {FOCA_LOCAL_GUIDE}"
    elif intent == "events":
        events = await db.events.find({"is_active": True}, {"_id": 0}).to_list(20)
        context = f"Aktif etkinlikler: {events}" if events else "Su anda aktif etkinlik bulunmuyor."

    response = await get_chat_response(
        message=data.message,
        session_id=data.session_id,
        system_prompt=GEMINI_SYSTEM_PROMPT,
        context=context,
    )

    # Save message to DB
    msg_record = {
        "id": new_id(),
        "session_id": data.session_id,
        "user_message": data.message,
        "ai_response": response,
        "intent": intent,
        "created_at": utcnow(),
    }
    await db.chat_messages.insert_one(msg_record)

    return {
        "response": response,
        "session_id": data.session_id,
        "intent": intent,
    }


@api.get("/chatbot/history/{session_id}")
async def chat_history(session_id: str):
    messages = await db.chat_messages.find(
        {"session_id": session_id}, {"_id": 0}
    ).sort("created_at", 1).to_list(100)
    return {"messages": messages}


@api.delete("/chatbot/session/{session_id}")
async def clear_chat(session_id: str):
    from gemini_service import clear_session
    clear_session(session_id)
    await db.chat_messages.delete_many({"session_id": session_id})
    return {"success": True}


# ==================== WHATSAPP WEBHOOK ====================

@api.post("/whatsapp/webhook")
async def whatsapp_webhook(data: WhatsAppMessage):
    from gemini_service import get_chat_response, detect_intent

    session_id = f"wa-{data.from_number}"
    intent = detect_intent(data.message)

    response = await get_chat_response(
        message=data.message,
        session_id=session_id,
        system_prompt=GEMINI_SYSTEM_PROMPT,
    )

    msg = {
        "id": new_id(),
        "platform": "whatsapp",
        "from_number": data.from_number,
        "sender_name": data.sender_name,
        "message": data.message,
        "response": response,
        "intent": intent,
        "created_at": utcnow(),
    }
    await db.messages.insert_one(msg)

    return {"reply": response, "intent": intent}


@api.get("/whatsapp/messages")
async def list_whatsapp_messages(limit: int = 50):
    msgs = await db.messages.find(
        {"platform": "whatsapp"}, {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    return {"messages": msgs}


# ==================== INSTAGRAM WEBHOOK ====================

@api.post("/instagram/webhook")
async def instagram_webhook(data: dict):
    from gemini_service import get_chat_response

    msg_text = data.get("message", "")
    sender = data.get("sender", "unknown")
    session_id = f"ig-{sender}"

    response = await get_chat_response(
        message=msg_text,
        session_id=session_id,
        system_prompt=GEMINI_SYSTEM_PROMPT,
    )

    msg = {
        "id": new_id(),
        "platform": "instagram",
        "sender": sender,
        "message": msg_text,
        "response": response,
        "created_at": utcnow(),
    }
    await db.messages.insert_one(msg)

    return {"reply": response}


@api.get("/messages")
async def list_all_messages(platform: Optional[str] = None, limit: int = 50):
    query = {"platform": platform} if platform else {}
    msgs = await db.messages.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    return {"messages": msgs}


# ==================== SEED DATA ====================

@api.post("/seed")
async def seed_database():
    """Seed initial hotel data into MongoDB"""
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


# ==================== SETUP ====================

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
    # Auto-seed on startup
    rooms_count = await db.rooms.count_documents({})
    if rooms_count == 0:
        for room in ROOMS:
            await db.rooms.insert_one({**room, "created_at": utcnow()})
        logger.info("Rooms seeded successfully")


@app.on_event("shutdown")
async def shutdown():
    client.close()
