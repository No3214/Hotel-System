from fastapi import APIRouter
from database import db
from helpers import clean_docs, new_id, utcnow
from hotel_data import HOTEL_INFO
from menu_seed_data import UPDATED_MENU_CATEGORIES, UPDATED_MENU_ITEMS

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


async def ensure_menu_seeded():
    """Seed or reseed menu data to MongoDB"""
    # Check version marker
    version = await db.theme_settings.find_one({"type": "qr_menu_version"}, {"_id": 0})
    current_version = "v3_full_menu"

    if version and version.get("version") == current_version:
        return

    # Clear and reseed
    await db.menu_items.delete_many({})
    await db.menu_categories.delete_many({})

    # Seed categories
    for cat in UPDATED_MENU_CATEGORIES:
        await db.menu_categories.insert_one({
            "id": new_id(),
            "key": cat["key"],
            "name_tr": cat["name_tr"],
            "name_en": cat["name_en"],
            "icon": cat["icon"],
            "sort_order": cat["sort_order"],
            "is_active": True,
            "created_at": utcnow(),
        })

    # Seed items
    for cat_key, items in UPDATED_MENU_ITEMS.items():
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

    # Seed theme if not exists
    existing_theme = await db.theme_settings.find_one({"type": "qr_menu"})
    if not existing_theme:
        await db.theme_settings.insert_one({**DEFAULT_THEME, "updated_at": utcnow()})

    # Update version marker
    await db.theme_settings.update_one(
        {"type": "qr_menu_version"},
        {"$set": {"type": "qr_menu_version", "version": current_version, "updated_at": utcnow()}},
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
    theme = await db.theme_settings.find_one({"type": "qr_menu"}, {"_id": 0})
    return theme or DEFAULT_THEME
