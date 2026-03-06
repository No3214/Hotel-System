"""
Kozbeyli Konagi - Content Queue & Smart Scheduling Service
Mixpost/Post4U'dan ilham: Tam ajans deneyimi

Ozellikler:
- Content Queue: Sira tabanlı gonderi kuyrugu
- Optimal Time: En iyi paylasim saatini hesapla
- Content Recycling: Basarili icerikeri tekrar paylas
- Weekly Planner: Haftalik icerik plani olustur
- Performance Scoring: Gonderi performans puanlama
"""
import logging
from typing import Optional, Dict, List
from datetime import datetime, timezone, timedelta
import random

logger = logging.getLogger(__name__)


# ==================== OPTIMAL POSTING TIMES ====================

# Turkiye'de sosyal medya kullanim istatistikleri (saat bazli engagement)
OPTIMAL_HOURS = {
    "instagram": {
        "weekday": [8, 12, 13, 17, 18, 19, 20, 21],  # Hafta ici
        "weekend": [10, 11, 12, 14, 15, 16, 19, 20],  # Hafta sonu
        "best": [12, 19, 20],  # En iyi saatler
    },
    "facebook": {
        "weekday": [9, 12, 13, 15, 17, 18, 19],
        "weekend": [10, 11, 12, 15, 16, 17],
        "best": [13, 17, 19],
    },
    "twitter": {
        "weekday": [8, 9, 12, 17, 18],
        "weekend": [9, 10, 12, 17],
        "best": [9, 12, 17],
    },
    "linkedin": {
        "weekday": [8, 9, 10, 12, 17],
        "weekend": [10, 11],
        "best": [9, 10, 12],
    },
}

# Otel sektoru icin ozel zamanlar
HOTEL_PEAK_TIMES = {
    "morning_coffee": {"hour": 8, "topics": ["morning", "behind_scenes"]},
    "lunch_promo": {"hour": 12, "topics": ["menu_highlight"]},
    "afternoon_dream": {"hour": 15, "topics": ["seasonal", "local", "weekend"]},
    "evening_mood": {"hour": 19, "topics": ["event", "guest_story"]},
    "night_plan": {"hour": 21, "topics": ["promo", "weekend"]},
}


def get_optimal_posting_time(platforms: List[str], topic: str = None) -> str:
    """
    Platformlar ve konu bazinda en iyi posting saatini hesapla.
    Returns: "HH:MM" format
    """
    now = datetime.now(timezone.utc)
    is_weekend = now.weekday() >= 5

    # Konu bazli ozel saat
    if topic:
        for _, peak in HOTEL_PEAK_TIMES.items():
            if topic in peak["topics"]:
                return f"{peak['hour']:02d}:00"

    # Platform bazli en iyi saat
    best_hours = set()
    for platform in platforms:
        platform_data = OPTIMAL_HOURS.get(platform, OPTIMAL_HOURS["instagram"])
        hours = platform_data["weekend" if is_weekend else "weekday"]
        best_hours.update(hours)

    if not best_hours:
        best_hours = {10, 13, 19}

    # Bugunun saatinden sonraki en yakin optimal saat
    current_hour = (now + timedelta(hours=3)).hour  # UTC+3 Istanbul
    future_hours = sorted(h for h in best_hours if h > current_hour)

    if future_hours:
        chosen = future_hours[0]
    else:
        # Yarin icin en iyi saat
        chosen = min(best_hours)

    # Dakika olarak rastgele ofset (tam saatte degil, dogal gorunsun)
    minute_offset = random.choice([0, 5, 10, 15, 30])

    return f"{chosen:02d}:{minute_offset:02d}"


# ==================== CONTENT QUEUE ====================

async def get_content_queue(limit: int = 20) -> List[Dict]:
    """Siradaki yayinlanacak gonderileri getir"""
    from database import db

    queue = await db.social_posts.find(
        {"status": {"$in": ["draft", "scheduled"]}, "queued": True},
        {"_id": 0}
    ).sort("queue_position", 1).limit(limit).to_list(limit)

    return queue


async def add_to_queue(post_id: str, position: int = None) -> Dict:
    """Gonderiyi kuyruga ekle"""
    from database import db
    from helpers import utcnow

    if position is None:
        # Son siraya ekle
        last = await db.social_posts.find_one(
            {"queued": True},
            {"_id": 0, "queue_position": 1},
            sort=[("queue_position", -1)]
        )
        position = (last.get("queue_position", 0) if last else 0) + 1

    await db.social_posts.update_one(
        {"id": post_id},
        {"$set": {"queued": True, "queue_position": position, "updated_at": utcnow()}}
    )

    return {"success": True, "position": position}


async def remove_from_queue(post_id: str) -> Dict:
    """Gonderiyi kuyruktan cikar"""
    from database import db
    from helpers import utcnow

    await db.social_posts.update_one(
        {"id": post_id},
        {"$set": {"queued": False, "queue_position": None, "updated_at": utcnow()}}
    )
    return {"success": True}


async def reorder_queue(post_ids: List[str]) -> Dict:
    """Kuyruk sirasini degistir"""
    from database import db
    from helpers import utcnow

    for idx, pid in enumerate(post_ids):
        await db.social_posts.update_one(
            {"id": pid},
            {"$set": {"queue_position": idx + 1, "updated_at": utcnow()}}
        )
    return {"success": True, "count": len(post_ids)}


# ==================== CONTENT RECYCLING ====================

async def get_recyclable_posts(min_days_old: int = 30, limit: int = 10) -> List[Dict]:
    """
    Mixpost'tan: Basarili eski gonderileri tekrar paylasim icin getir.
    Kriterler: 30+ gun once yayinlanmis, yuksek performansli
    """
    from database import db

    cutoff = (datetime.now(timezone.utc) - timedelta(days=min_days_old)).isoformat()

    recyclable = await db.social_posts.find(
        {
            "status": "published",
            "published_at": {"$lte": cutoff},
            "recycled": {"$ne": True},
            "source": {"$ne": "recycled"},
        },
        {"_id": 0}
    ).sort("published_at", 1).limit(limit).to_list(limit)

    return recyclable


async def recycle_post(post_id: str, new_platforms: List[str] = None) -> Dict:
    """Eski gonderiyi yeni gonderi olarak tekrar olustur"""
    from database import db
    from helpers import utcnow, new_id

    original = await db.social_posts.find_one({"id": post_id}, {"_id": 0})
    if not original:
        return {"success": False, "error": "Gonderi bulunamadi"}

    # Yeni gonderi olustur
    recycled = {
        "id": new_id(),
        "title": original.get("title", ""),
        "content": original.get("content", ""),
        "platforms": new_platforms or original.get("platforms", []),
        "post_type": original.get("post_type", "text"),
        "frame_style": original.get("frame_style", "default"),
        "hashtags": original.get("hashtags", []),
        "image_url": original.get("image_url"),
        "status": "draft",
        "source": "recycled",
        "original_post_id": post_id,
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }

    await db.social_posts.insert_one(recycled)

    # Orijinali isaretl
    await db.social_posts.update_one(
        {"id": post_id},
        {"$set": {"recycled": True, "recycled_at": utcnow()}}
    )

    return {"success": True, "new_post": recycled}


# ==================== WEEKLY PLANNER ====================

WEEKLY_TEMPLATE = {
    0: {"topic": "morning", "label": "Pazartesi - Motivasyon & Gunaydin"},
    1: {"topic": "menu_highlight", "label": "Sali - Lezzet Vitrini"},
    2: {"topic": "local", "label": "Carsamba - Foca & Cevre Rehberi"},
    3: {"topic": "behind_scenes", "label": "Persembe - Sahne Arkasi"},
    4: {"topic": "guest_story", "label": "Cuma - Misafir Deneyimleri"},
    5: {"topic": "weekend", "label": "Cumartesi - Hafta Sonu Kacamagi"},
    6: {"topic": "seasonal", "label": "Pazar - Mevsimsel Icerik"},
}


async def generate_weekly_plan(start_date: str = None) -> Dict:
    """
    Haftalik icerik plani olustur.
    Her gun icin konu + optimal saat + platform onerisi.
    """
    from helpers import utcnow

    if not start_date:
        today = datetime.now(timezone.utc)
        # Bu haftanin pazartesisini bul
        start = today - timedelta(days=today.weekday())
        start_date = start.strftime("%Y-%m-%d")

    plan = []
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")

    for day_offset in range(7):
        date = start_dt + timedelta(days=day_offset)
        day_of_week = date.weekday()
        template = WEEKLY_TEMPLATE.get(day_of_week, WEEKLY_TEMPLATE[0])

        platforms = ["instagram", "facebook"]
        optimal_time = get_optimal_posting_time(platforms, template["topic"])

        plan.append({
            "date": date.strftime("%Y-%m-%d"),
            "day_name": ["Pzt", "Sal", "Car", "Per", "Cum", "Cmt", "Paz"][day_of_week],
            "topic": template["topic"],
            "label": template["label"],
            "platforms": platforms,
            "optimal_time": optimal_time,
            "status": "planned",
        })

    return {
        "week_start": start_date,
        "plan": plan,
        "created_at": utcnow(),
    }


# ==================== PERFORMANCE SCORING ====================

async def calculate_post_performance(post_id: str) -> Dict:
    """
    Gonderi performans puani hesapla.
    Skor 0-100 arasi, icerik uzunlugu + hashtag sayisi + platform sayisi + zamanlama
    """
    from database import db

    post = await db.social_posts.find_one({"id": post_id}, {"_id": 0})
    if not post:
        return {"score": 0, "error": "Gonderi bulunamadi"}

    score = 0
    details = {}

    # Icerik uzunlugu (ideal: 150-300 karakter)
    content_len = len(post.get("content", ""))
    if 150 <= content_len <= 300:
        score += 25
        details["content_length"] = "ideal"
    elif 100 <= content_len <= 400:
        score += 15
        details["content_length"] = "good"
    else:
        score += 5
        details["content_length"] = "needs_improvement"

    # Hashtag sayisi (ideal: 5-10)
    hashtag_count = len(post.get("hashtags", []))
    if 5 <= hashtag_count <= 10:
        score += 20
        details["hashtags"] = "ideal"
    elif 3 <= hashtag_count <= 15:
        score += 10
        details["hashtags"] = "good"
    else:
        score += 5
        details["hashtags"] = "needs_improvement"

    # Gorsel var mi
    if post.get("image_url"):
        score += 20
        details["has_image"] = True
    else:
        details["has_image"] = False

    # Platform sayisi
    platform_count = len(post.get("platforms", []))
    score += min(15, platform_count * 5)
    details["platforms"] = platform_count

    # Baslik var mi
    if post.get("title") and len(post["title"]) > 5:
        score += 10
        details["has_title"] = True
    else:
        details["has_title"] = False

    # Zamanlama puani (scheduled vs draft)
    if post.get("status") == "scheduled" and post.get("scheduled_at"):
        score += 10
        details["scheduled"] = True
    else:
        details["scheduled"] = False

    return {
        "post_id": post_id,
        "score": min(100, score),
        "grade": "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "D",
        "details": details,
    }
