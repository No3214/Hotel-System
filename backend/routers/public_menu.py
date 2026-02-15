from fastapi import APIRouter
from database import db
from helpers import clean_docs
from hotel_data import RESTAURANT_MENU, HOTEL_INFO

router = APIRouter(tags=["public-menu"])

DEFAULT_THEME = {
    "type": "qr_menu",
    "brand_name": "Kozbeyli Konagi",
    "tagline": "Tas Otel",
    "logo_url": "/brand/KOZBEYLI_BEYAZ_LOGO.png",
    "font_heading": "Alifira",
    "font_body": "Inter",
    "colors": {
        "bg": "#515249",
        "text": "#F8F5EF",
        "muted": "#D8D1C5",
        "card": "#F3EEE4",
        "border": "#6A6B60",
        "primary": "#8FAA86",
        "on_primary": "#1E1B16",
        "accent": "#B07A2A",
        "on_accent": "#1E1B16",
        "link": "#A9C3A2",
    },
    "background": {
        "mode": "gradient",
        "value": "linear-gradient(180deg, #3F403A 0%, #515249 55%, #3F403A 100%)",
        "overlayOpacity": 0.0,
    },
    "components": {
        "radius": 18,
        "shadow": "soft",
        "buttonStyle": "filled",
        "cardStyle": "clean",
        "headingUppercase": True,
        "headingTracking": 0.12,
    },
    "layout": {
        "header": {
            "style": "solid",
            "height": 220,
            "showLogo": True,
            "logoMaxWidth": 320,
            "center": True,
        },
        "menu": {
            "categoryTitleStyle": "uppercase",
            "categoryGridDesktopCols": 2,
            "categoryGridMobileCols": 1,
        },
    },
}

DEFAULT_CATEGORIES = [
    {"key": "kahvalti", "name_tr": "Kahvalti", "name_en": "Breakfast", "icon": "utensils", "sort_order": 0, "is_active": True},
    {"key": "baslangic", "name_tr": "Baslangiclar", "name_en": "Starters", "icon": "salad", "sort_order": 1, "is_active": True},
    {"key": "meze", "name_tr": "Mezeler", "name_en": "Appetizers", "icon": "leaf", "sort_order": 2, "is_active": True},
    {"key": "ana_yemek", "name_tr": "Ana Yemekler", "name_en": "Main Courses", "icon": "flame", "sort_order": 3, "is_active": True},
    {"key": "pizza_sandvic", "name_tr": "Pizza & Sandvic", "name_en": "Pizza & Sandwich", "icon": "pizza", "sort_order": 4, "is_active": True},
    {"key": "tatli", "name_tr": "Tatlilar", "name_en": "Desserts", "icon": "cake", "sort_order": 5, "is_active": True},
    {"key": "sicak_icecekler", "name_tr": "Sicak Icecekler", "name_en": "Hot Drinks", "icon": "coffee", "sort_order": 6, "is_active": True},
    {"key": "soguk_icecekler", "name_tr": "Soguk Icecekler", "name_en": "Cold Drinks", "icon": "glass-water", "sort_order": 7, "is_active": True},
    {"key": "sarap", "name_tr": "Saraplar", "name_en": "Wines", "icon": "wine", "sort_order": 8, "is_active": True},
    {"key": "bira", "name_tr": "Biralar", "name_en": "Beers", "icon": "beer", "sort_order": 9, "is_active": True},
    {"key": "raki", "name_tr": "Raki", "name_en": "Raki", "icon": "glass", "sort_order": 10, "is_active": True},
    {"key": "viski", "name_tr": "Viskiler", "name_en": "Whiskies", "icon": "whiskey", "sort_order": 11, "is_active": True},
    {"key": "kokteyl", "name_tr": "Kokteyller", "name_en": "Cocktails", "icon": "cocktail", "sort_order": 12, "is_active": True},
]


async def ensure_menu_seeded():
    """Seed menu data to MongoDB if not present"""
    count = await db.menu_items.count_documents({})
    if count > 0:
        return

    from helpers import new_id, utcnow

    # Seed categories
    for cat in DEFAULT_CATEGORIES:
        await db.menu_categories.insert_one({
            **cat,
            "id": new_id(),
            "created_at": utcnow(),
        })

    # Seed items from RESTAURANT_MENU
    for cat_key, items in RESTAURANT_MENU.items():
        for i, item in enumerate(items):
            await db.menu_items.insert_one({
                "id": new_id(),
                "category": cat_key,
                "name": item["name"],
                "desc": item.get("desc", ""),
                "price_try": item["price_try"],
                "is_available": True,
                "sort_order": i,
                "created_at": utcnow(),
                "updated_at": utcnow(),
            })

    # Seed theme
    await db.theme_settings.update_one(
        {"type": "qr_menu"},
        {"$set": {**DEFAULT_THEME, "updated_at": utcnow()}},
        upsert=True,
    )


@router.get("/public/menu")
async def get_public_menu():
    """Public endpoint - no auth required"""
    await ensure_menu_seeded()

    theme = await db.theme_settings.find_one({"type": "qr_menu"}, {"_id": 0})
    if not theme:
        theme = DEFAULT_THEME

    categories = await db.menu_categories.find(
        {"is_active": True}, {"_id": 0}
    ).sort("sort_order", 1).to_list(50)

    items = await db.menu_items.find(
        {"is_available": True}, {"_id": 0}
    ).sort("sort_order", 1).to_list(500)

    # Group items by category
    menu = {}
    for cat in categories:
        cat_items = [it for it in items if it["category"] == cat["key"]]
        if cat_items:
            menu[cat["key"]] = {
                "name_tr": cat["name_tr"],
                "name_en": cat.get("name_en", cat["name_tr"]),
                "icon": cat.get("icon", "utensils"),
                "items": cat_items,
            }

    return {
        "theme": theme,
        "menu": menu,
        "restaurant": HOTEL_INFO["restaurant_name"],
        "hotel": HOTEL_INFO["name"],
    }


@router.get("/public/theme")
async def get_public_theme():
    """Public endpoint for theme only"""
    theme = await db.theme_settings.find_one({"type": "qr_menu"}, {"_id": 0})
    return theme or DEFAULT_THEME
