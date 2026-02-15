from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from database import db
from helpers import utcnow, new_id, clean_doc

router = APIRouter(tags=["menu-admin"])


class MenuItemCreate(BaseModel):
    category: str
    name: str
    desc: str = ""
    price_try: float
    is_available: bool = True
    sort_order: int = 0


class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    desc: Optional[str] = None
    price_try: Optional[float] = None
    is_available: Optional[bool] = None
    sort_order: Optional[int] = None
    category: Optional[str] = None


class CategoryCreate(BaseModel):
    key: str
    name_tr: str
    name_en: str = ""
    icon: str = "utensils"
    sort_order: int = 0
    is_active: bool = True


# ---- ITEMS ----

@router.get("/menu-admin/items")
async def list_menu_items(category: Optional[str] = None):
    query = {}
    if category:
        query["category"] = category
    items = await db.menu_items.find(query, {"_id": 0}).sort("sort_order", 1).to_list(500)
    return {"items": items}


@router.post("/menu-admin/items")
async def create_menu_item(data: MenuItemCreate):
    item = {
        "id": new_id(),
        **data.model_dump(),
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }
    await db.menu_items.insert_one(item)
    return clean_doc(item)


@router.patch("/menu-admin/items/{item_id}")
async def update_menu_item(item_id: str, data: MenuItemUpdate):
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(400, "Guncellenecek alan yok")
    updates["updated_at"] = utcnow()
    result = await db.menu_items.update_one({"id": item_id}, {"$set": updates})
    if result.matched_count == 0:
        raise HTTPException(404, "Menu ogesi bulunamadi")
    item = await db.menu_items.find_one({"id": item_id}, {"_id": 0})
    return item


@router.delete("/menu-admin/items/{item_id}")
async def delete_menu_item(item_id: str):
    result = await db.menu_items.delete_one({"id": item_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Menu ogesi bulunamadi")
    return {"success": True}


# ---- CATEGORIES ----

@router.get("/menu-admin/categories")
async def list_categories():
    cats = await db.menu_categories.find({}, {"_id": 0}).sort("sort_order", 1).to_list(50)
    return {"categories": cats}


@router.post("/menu-admin/categories")
async def create_category(data: CategoryCreate):
    existing = await db.menu_categories.find_one({"key": data.key})
    if existing:
        raise HTTPException(409, "Bu kategori anahtari zaten mevcut")
    cat = {
        "id": new_id(),
        **data.model_dump(),
        "created_at": utcnow(),
    }
    await db.menu_categories.insert_one(cat)
    return clean_doc(cat)


@router.patch("/menu-admin/categories/{cat_id}")
async def update_category(cat_id: str, data: dict):
    data.pop("id", None)
    data.pop("_id", None)
    if not data:
        raise HTTPException(400, "Guncellenecek alan yok")
    result = await db.menu_categories.update_one({"id": cat_id}, {"$set": data})
    if result.matched_count == 0:
        raise HTTPException(404, "Kategori bulunamadi")
    cat = await db.menu_categories.find_one({"id": cat_id}, {"_id": 0})
    return cat


@router.delete("/menu-admin/categories/{cat_id}")
async def delete_category(cat_id: str):
    cat = await db.menu_categories.find_one({"id": cat_id}, {"_id": 0})
    if not cat:
        raise HTTPException(404, "Kategori bulunamadi")
    await db.menu_items.delete_many({"category": cat["key"]})
    await db.menu_categories.delete_one({"id": cat_id})
    return {"success": True}


# ---- THEME ----

@router.get("/menu-admin/theme")
async def get_theme():
    theme = await db.theme_settings.find_one({"type": "qr_menu"}, {"_id": 0})
    if not theme:
        from routers.public_menu import DEFAULT_THEME
        return DEFAULT_THEME
    return theme


@router.patch("/menu-admin/theme")
async def update_theme(data: dict):
    data.pop("_id", None)
    data["type"] = "qr_menu"
    data["updated_at"] = utcnow()
    await db.theme_settings.update_one(
        {"type": "qr_menu"},
        {"$set": data},
        upsert=True,
    )
    theme = await db.theme_settings.find_one({"type": "qr_menu"}, {"_id": 0})
    return theme
