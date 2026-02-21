from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional
from database import db
from helpers import utcnow, new_id
from passlib.context import CryptContext
import jwt
import os
import time
import secrets
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth"])

# JWT Configuration — secret MUST come from environment in production
_default_secret = secrets.token_hex(32)
SECRET_KEY = os.environ.get("JWT_SECRET", _default_secret)
if SECRET_KEY == _default_secret:
    logger.warning("JWT_SECRET not set in environment — using random secret. Tokens will NOT survive restarts.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = int(os.environ.get("JWT_EXPIRE_SECONDS", 86400))  # 24 hours default
REFRESH_TOKEN_EXPIRE_SECONDS = int(os.environ.get("JWT_REFRESH_EXPIRE_SECONDS", 604800))  # 7 days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ROLES = {
    "admin": {"label": "Admin", "permissions": ["*"]},
    "reception": {"label": "Resepsiyon", "permissions": ["reservations", "guests", "rooms", "tasks", "table_reservations", "messages", "lifecycle", "housekeeping", "dashboard", "pricing"]},
    "kitchen": {"label": "Mutfak", "permissions": ["table_reservations", "menu", "tasks", "housekeeping", "kitchen"]},
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


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


def create_token(user_id: str, username: str, role: str, token_type: str = "access") -> str:
    """Create a JWT token with expiration"""
    if token_type == "refresh":
        expire = int(time.time()) + REFRESH_TOKEN_EXPIRE_SECONDS
    else:
        expire = int(time.time()) + ACCESS_TOKEN_EXPIRE_SECONDS

    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "type": token_type,
        "iat": int(time.time()),
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") == "refresh":
            raise HTTPException(401, "Refresh token'i erisim icin kullanilamaz")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token suresi dolmus — lutfen tekrar giris yapin")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Gecersiz token")


async def get_current_user(request: Request) -> dict:
    """Extract and verify user from Authorization header"""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(401, "Yetkilendirme basarisi gerekli")
    token = auth_header.split(" ")[1]
    return verify_token(token)


async def require_admin(request: Request) -> dict:
    """Require admin role"""
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(403, "Bu islem icin admin yetkisi gerekli")
    return user


@router.post("/auth/login")
async def login(data: LoginRequest, request: Request):
    from rate_limiter import rate_limit_or_raise, get_client_identifier
    # Rate limit login attempts
    identifier = get_client_identifier(request)
    rate_limit_or_raise(request, "login")

    user = await db.users.find_one({"username": data.username}, {"_id": 0})
    if not user or not pwd_context.verify(data.password, user["password_hash"]):
        logger.warning(f"Failed login attempt for username: {data.username} from {identifier}")
        raise HTTPException(401, "Kullanici adi veya sifre hatali")

    if not user.get("is_active", True):
        raise HTTPException(403, "Hesabiniz devre disi birakilmis")

    access_token = create_token(user["id"], user["username"], user["role"], "access")
    refresh_token = create_token(user["id"], user["username"], user["role"], "refresh")

    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"last_login": utcnow()}}
    )

    logger.info(f"Successful login: {data.username}")

    return {
        "token": access_token,
        "refresh_token": refresh_token,
        "expires_in": ACCESS_TOKEN_EXPIRE_SECONDS,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "name": user["name"],
            "role": user["role"],
            "permissions": ROLES.get(user["role"], {}).get("permissions", []),
        },
    }


@router.post("/auth/refresh")
async def refresh_token(data: RefreshTokenRequest):
    """Get a new access token using a refresh token"""
    try:
        payload = jwt.decode(data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(401, "Gecersiz refresh token")

        user = await db.users.find_one({"id": payload["user_id"]}, {"_id": 0})
        if not user or not user.get("is_active", True):
            raise HTTPException(401, "Kullanici bulunamadi veya devre disi")

        access_token = create_token(user["id"], user["username"], user["role"], "access")
        return {
            "token": access_token,
            "expires_in": ACCESS_TOKEN_EXPIRE_SECONDS,
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Refresh token suresi dolmus — tekrar giris yapin")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Gecersiz refresh token")


@router.get("/auth/me")
async def get_me(request: Request):
    payload = await get_current_user(request)
    user = await db.users.find_one({"id": payload["user_id"]}, {"_id": 0, "password_hash": 0})
    if not user:
        raise HTTPException(404, "Kullanici bulunamadi")
    user["permissions"] = ROLES.get(user.get("role", "staff"), {}).get("permissions", [])
    return user


@router.post("/auth/change-password")
async def change_password(data: ChangePasswordRequest, request: Request):
    """Change current user's password"""
    payload = await get_current_user(request)
    user = await db.users.find_one({"id": payload["user_id"]}, {"_id": 0})
    if not user:
        raise HTTPException(404, "Kullanici bulunamadi")

    if not pwd_context.verify(data.current_password, user["password_hash"]):
        raise HTTPException(400, "Mevcut sifre hatali")

    if len(data.new_password) < 8:
        raise HTTPException(400, "Yeni sifre en az 8 karakter olmali")

    new_hash = pwd_context.hash(data.new_password)
    await db.users.update_one(
        {"id": payload["user_id"]},
        {"$set": {"password_hash": new_hash, "password_changed_at": utcnow()}}
    )

    logger.info(f"Password changed for user: {payload['username']}")
    return {"success": True, "message": "Sifre basariyla degistirildi"}


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

    if len(data.password) < 8:
        raise HTTPException(400, "Sifre en az 8 karakter olmali")

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

    logger.info(f"New user created: {data.username} (role: {data.role})")
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
    logger.info(f"User deleted: {user_id} by {payload['username']}")
    return {"success": True}


@router.patch("/auth/users/{user_id}/toggle-active")
async def toggle_user_active(user_id: str, request: Request):
    """Activate or deactivate a user account"""
    payload = await get_current_user(request)
    if payload.get("role") != "admin":
        raise HTTPException(403, "Sadece admin bu islemi yapabilir")
    if payload.get("user_id") == user_id:
        raise HTTPException(400, "Kendi hesabinizi devre disi birakamazsiniz")

    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(404, "Kullanici bulunamadi")

    new_status = not user.get("is_active", True)
    await db.users.update_one({"id": user_id}, {"$set": {"is_active": new_status}})

    status_text = "aktif" if new_status else "devre disi"
    logger.info(f"User {user_id} set to {status_text} by {payload['username']}")
    return {"success": True, "is_active": new_status, "message": f"Kullanici {status_text}"}


@router.get("/auth/roles")
async def get_roles():
    return {"roles": [{**v, "key": k} for k, v in ROLES.items()]}


@router.post("/auth/setup")
async def initial_setup():
    """Create default admin if no users exist — password must be changed immediately"""
    count = await db.users.count_documents({})
    if count > 0:
        return {"message": "Sistem zaten kurulmus", "has_users": True}

    # Generate a random initial password
    initial_password = secrets.token_urlsafe(16)

    admin = {
        "id": new_id(),
        "username": "admin",
        "password_hash": pwd_context.hash(initial_password),
        "name": "Sistem Yoneticisi",
        "role": "admin",
        "email": "info@kozbeylikonagi.com",
        "phone": "+90 232 812 22 50",
        "is_active": True,
        "must_change_password": True,
        "created_at": utcnow(),
        "last_login": None,
    }
    await db.users.insert_one(admin)

    logger.info("Initial admin setup completed")
    return {
        "message": "Admin kullanici olusturuldu",
        "username": "admin",
        "password": initial_password,
        "warning": "Bu sifre sadece bir kez gosterilecek! Hemen degistirin.",
    }
