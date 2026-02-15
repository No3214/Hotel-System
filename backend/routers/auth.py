from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional
from database import db
from helpers import utcnow, new_id
from passlib.context import CryptContext
import jwt
import os

router = APIRouter(tags=["auth"])

SECRET_KEY = os.environ.get("JWT_SECRET", "kozbeyli-konagi-secret-2026")
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ROLES = {
    "admin": {"label": "Admin", "permissions": ["*"]},
    "reception": {"label": "Resepsiyon", "permissions": ["reservations", "guests", "rooms", "tasks", "table_reservations", "messages", "lifecycle", "housekeeping", "dashboard"]},
    "kitchen": {"label": "Mutfak", "permissions": ["table_reservations", "menu", "tasks", "housekeeping"]},
    "staff": {"label": "Personel", "permissions": ["tasks", "housekeeping", "dashboard"]},
}


class LoginRequest(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    password: str
    name: str
    role: str = "staff"
    email: Optional[str] = None
    phone: Optional[str] = None


def create_token(user_id: str, username: str, role: str) -> str:
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Gecersiz veya suresi dolmus token")


async def get_current_user(request: Request) -> dict:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(401, "Yetkilendirme basarisi gerekli")
    token = auth_header.split(" ")[1]
    return verify_token(token)


@router.post("/auth/login")
async def login(data: LoginRequest):
    user = await db.users.find_one({"username": data.username}, {"_id": 0})
    if not user or not pwd_context.verify(data.password, user["password_hash"]):
        raise HTTPException(401, "Kullanici adi veya sifre hatali")

    token = create_token(user["id"], user["username"], user["role"])

    await db.users.update_one({"id": user["id"]}, {"$set": {"last_login": utcnow()}})

    return {
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "name": user["name"],
            "role": user["role"],
            "permissions": ROLES.get(user["role"], {}).get("permissions", []),
        },
    }


@router.get("/auth/me")
async def get_me(request: Request):
    payload = await get_current_user(request)
    user = await db.users.find_one({"id": payload["user_id"]}, {"_id": 0, "password_hash": 0})
    if not user:
        raise HTTPException(404, "Kullanici bulunamadi")
    user["permissions"] = ROLES.get(user.get("role", "staff"), {}).get("permissions", [])
    return user


@router.post("/auth/register")
async def register_user(data: UserCreate, request: Request):
    # Only admin can create users
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        payload = verify_token(auth_header.split(" ")[1])
        if payload.get("role") != "admin":
            raise HTTPException(403, "Sadece admin kullanici olusturabilir")
    else:
        # Check if this is the first user (bootstrap)
        count = await db.users.count_documents({})
        if count > 0:
            raise HTTPException(403, "Yetkilendirme gerekli")

    if data.role not in ROLES:
        raise HTTPException(400, f"Gecersiz rol. Gecerli roller: {list(ROLES.keys())}")

    existing = await db.users.find_one({"username": data.username})
    if existing:
        raise HTTPException(409, "Bu kullanici adi zaten mevcut")

    user = {
        "id": new_id(),
        "username": data.username,
        "password_hash": pwd_context.hash(data.password),
        "name": data.name,
        "role": data.role,
        "email": data.email,
        "phone": data.phone,
        "is_active": True,
        "created_at": utcnow(),
        "last_login": None,
    }
    await db.users.insert_one(user)
    del user["password_hash"]
    if "_id" in user:
        del user["_id"]
    return user


@router.get("/auth/users")
async def list_users(request: Request):
    payload = await get_current_user(request)
    if payload.get("role") != "admin":
        raise HTTPException(403, "Sadece admin kullanicilari gorebilir")
    users = await db.users.find({}, {"_id": 0, "password_hash": 0}).to_list(100)
    return {"users": users}


@router.delete("/auth/users/{user_id}")
async def delete_user(user_id: str, request: Request):
    payload = await get_current_user(request)
    if payload.get("role") != "admin":
        raise HTTPException(403, "Sadece admin kullanici silebilir")
    if payload.get("user_id") == user_id:
        raise HTTPException(400, "Kendinizi silemezsiniz")
    result = await db.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Kullanici bulunamadi")
    return {"success": True}


@router.get("/auth/roles")
async def get_roles():
    return {"roles": [{**v, "key": k} for k, v in ROLES.items()]}


@router.post("/auth/setup")
async def initial_setup():
    """Create default admin if no users exist"""
    count = await db.users.count_documents({})
    if count > 0:
        return {"message": "Sistem zaten kurulmus", "has_users": True}

    admin = {
        "id": new_id(),
        "username": "admin",
        "password_hash": pwd_context.hash("kozbeyli2026"),
        "name": "Sistem Yoneticisi",
        "role": "admin",
        "email": "info@kozbeylikonagi.com",
        "phone": "+90 232 812 22 50",
        "is_active": True,
        "created_at": utcnow(),
        "last_login": None,
    }
    await db.users.insert_one(admin)
    return {
        "message": "Admin kullanici olusturuldu",
        "username": "admin",
        "password": "kozbeyli2026",
        "warning": "Lutfen sifrenizi hemen degistirin!",
    }
