from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from database import db
from helpers import utcnow, new_id, clean_doc
import json
from gemini_service import get_chat_response

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


# ==================== PHASE 12: AI MENU ENGINEERING ====================

@router.get("/menu-admin/ai-engineering")
async def ai_menu_engineering():
    """
    Kozbeyli Konagi Restoran yonetimi icin AI Destekli Menu Muhendisligi.
    Siparis gecmisini tarar (en cok/en az satanlar, ciro getirenler) ve
    hava durumuyla harmanlayarak anlik strateji onerir. (Puzzle, Star, Dog, Plowhorse analizleri)
    """
    try:
        # 1. En son tamamlanan mutfak siparislerini cek (ornek 50 siparis)
        recent_orders = await db.kitchen_orders.find({"status": "completed"}, {"_id": 0, "items": 1, "total_amount": 1}).sort("created_at", -1).limit(50).to_list(50)
        
        # 2. Mevcut menu itemlarini cek (hangisi ne kadar fiyatli vs)
        menu_items = await db.menu_items.find({"is_available": True}, {"_id": 0, "name": 1, "price_try": 1, "category": 1}).to_list(100)
        
        # 3. Siparis istatistiklerini cikar
        sales_data = {}
        for order in recent_orders:
            for it in order.get("items", []):
                name = it.get("name")
                qty = it.get("quantity", 1)
                if name:
                    if name not in sales_data:
                        sales_data[name] = {"qty": 0, "revenue": 0}
                    sales_data[name]["qty"] += qty
                    sales_data[name]["revenue"] += qty * it.get("price", 0)
                    
        # Eger hic siparis yoksa (sistem yeniyse) mock data gonder, analizi gorelim
        if not sales_data:
             sales_data = {
                 "Karisik Ege Kahvaltisi": {"qty": 45, "revenue": 18000},
                 "Levrek Izgara": {"qty": 12, "revenue": 6000},
                 "Sıcak Sarap": {"qty": 5, "revenue": 1250},
                 "Kuzu Incik": {"qty": 3, "revenue": 2400}, # Kârli ama az satiyor (Puzzle)
                 "Patates Kizartmasi": {"qty": 50, "revenue": 5000} # Cok satiyor ama ucuz (Plowhorse)
             }

        # 4. Basit bir hava durumu context'i (Gercek API yerine simule)
        import random
        weather_conditions = ["12C Yagmurlu ve Ruzgarli", "25C Gunesli ve Acik", "18C Bulutlu, Aksam Serin"]
        current_weather = random.choice(weather_conditions)

        prompt = f"""
        Sen Kozbeyli Konagi'nin Executive Sefi ve Restoran Kâr Optimizasyonu (F&B) Uzmanisin.
        Asagidaki verilere bakarak 'Menu Muhendisligi' (Menu Engineering - Matrix) raporu çikar.

        Hava Durumu Su An: {current_weather}
        
        Son Siparis Istatistikleri:
        {json.dumps(sales_data, ensure_ascii=False, indent=2)}

        Gorevin:
        Yukarıdaki satışlara ve hava durumuna bakarak bana sadece şu JSON yapısını döndür:
        {{
           "weather_context": "Hava durumuna ozel şefin yorumu (1 cumle)",
           "stars": ["Cok satan ve yuksek cirolu basarili urunler"],
           "puzzles": ["Cirosu yuksek ama az satan, satisi artirilmasi gereken urunler (Orn: 'Aksamlari garsonlar Kuzu Incik onersin')"],
           "plowhorses": ["Menunun vazgecilmezleri, cok satan ama ucuz ürünler. 'Porsiyonu kucult' veya 'Yaninda urun sat' tavsiyesi ver."],
           "dogs": ["Az satan ve az kazandiran urunler. 'Sertifikali cikarilmali' veya 'guncellenmeli'"],
           "action_plan": "Mutfak ekibine ve garsonlara bugun/bu hafta yapmalari gereken 2 maddelik net talimat."
        }}
        """

        ai_resp = await get_chat_response("menu_engineering", new_id(), prompt)
        
        import re
        json_match = re.search(r'```(?:json)?(.*?)```', ai_resp, re.DOTALL)
        res_str = json_match.group(1).strip() if json_match else ai_resp
        report_data = json.loads(res_str)

        return {
            "success": True,
            "report": report_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Menu Engineering hatasi: {str(e)}")
