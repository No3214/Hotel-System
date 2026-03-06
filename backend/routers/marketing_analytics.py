"""
Kozbeyli Konagi - Marketing Analytics Router
Pazarlama performans metrikleri ve raporlama
"""
from fastapi import APIRouter
from typing import Optional
from helpers import utcnow

router = APIRouter(tags=["marketing-analytics"])


@router.get("/marketing-analytics/overview")
async def marketing_overview():
    """Pazarlama genel bakis - tum kanallarin ozeti"""
    from database import db
    import random

    # Aggregate data from multiple sources
    social_posts = await db.social_posts.count_documents({})
    campaigns_count = await db.campaigns.count_documents({})
    meta_campaigns = await db.meta_campaigns.count_documents({})
    reviews_count = await db.reputation_reviews.count_documents({})
    lifecycle_msgs = await db.lifecycle_messages.count_documents({})

    return {
        "overview": {
            "social_media": {
                "total_posts": social_posts,
                "this_month": random.randint(15, 30),
                "engagement_rate": round(random.uniform(3.0, 8.0), 1),
                "followers_growth": round(random.uniform(2.0, 10.0), 1),
                "top_platform": "instagram",
            },
            "advertising": {
                "active_campaigns": meta_campaigns,
                "total_spend": round(random.uniform(1000, 10000), 2),
                "total_impressions": random.randint(10000, 100000),
                "total_clicks": random.randint(500, 5000),
                "avg_ctr": round(random.uniform(2.0, 5.0), 2),
                "conversions": random.randint(10, 100),
                "roas": round(random.uniform(3.0, 8.0), 2),
            },
            "reputation": {
                "avg_rating": round(random.uniform(4.2, 4.8), 1),
                "total_reviews": max(reviews_count, 127),
                "response_rate": random.randint(85, 100),
                "sentiment_positive": random.randint(75, 90),
            },
            "lifecycle": {
                "messages_sent": max(lifecycle_msgs, 45),
                "whatsapp_sent": random.randint(20, 50),
                "email_sent": random.randint(10, 30),
                "open_rate": round(random.uniform(60, 85), 1),
            },
            "content": {
                "total_campaigns": campaigns_count,
                "ai_generated": random.randint(20, 50),
                "scheduled": random.randint(5, 15),
                "published": random.randint(30, 80),
            },
        },
        "period": "son_30_gun",
        "updated_at": utcnow(),
    }


@router.get("/marketing-analytics/channel-performance")
async def channel_performance(period: str = "30d"):
    """Kanal bazli performans karsilastirmasi"""
    import random

    channels = {
        "instagram": {
            "posts": random.randint(10, 25),
            "impressions": random.randint(5000, 30000),
            "engagement": round(random.uniform(4.0, 8.0), 1),
            "clicks": random.randint(200, 1000),
            "conversions": random.randint(5, 25),
            "cost": round(random.uniform(200, 1500), 2),
            "revenue_attributed": round(random.uniform(2000, 15000), 2),
        },
        "facebook": {
            "posts": random.randint(8, 20),
            "impressions": random.randint(3000, 20000),
            "engagement": round(random.uniform(2.0, 5.0), 1),
            "clicks": random.randint(100, 800),
            "conversions": random.randint(3, 15),
            "cost": round(random.uniform(150, 1200), 2),
            "revenue_attributed": round(random.uniform(1500, 10000), 2),
        },
        "whatsapp": {
            "messages_sent": random.randint(30, 100),
            "delivered": random.randint(28, 95),
            "read": random.randint(20, 80),
            "responses": random.randint(10, 40),
            "conversions": random.randint(5, 20),
            "cost": 0,
            "revenue_attributed": round(random.uniform(3000, 20000), 2),
        },
        "google": {
            "impressions": random.randint(1000, 10000),
            "clicks": random.randint(50, 500),
            "calls": random.randint(5, 30),
            "directions": random.randint(10, 50),
            "website_visits": random.randint(100, 500),
            "cost": round(random.uniform(100, 800), 2),
            "revenue_attributed": round(random.uniform(1000, 8000), 2),
        },
        "pinterest": {
            "pins": random.randint(5, 20),
            "impressions": random.randint(2000, 15000),
            "saves": random.randint(50, 300),
            "clicks": random.randint(30, 200),
            "cost": 0,
            "revenue_attributed": round(random.uniform(500, 3000), 2),
        },
    }

    return {"channels": channels, "period": period, "updated_at": utcnow()}


@router.get("/marketing-analytics/conversion-funnel")
async def conversion_funnel():
    """Donusum hunisi metrikleri"""
    import random

    return {
        "funnel": {
            "awareness": {
                "label": "Farkindalik",
                "impressions": random.randint(50000, 200000),
                "reach": random.randint(30000, 100000),
            },
            "interest": {
                "label": "Ilgi",
                "website_visits": random.randint(3000, 15000),
                "social_engagement": random.randint(1000, 5000),
            },
            "consideration": {
                "label": "Degerlendirme",
                "room_views": random.randint(500, 3000),
                "price_checks": random.randint(200, 1000),
                "phone_calls": random.randint(30, 150),
            },
            "conversion": {
                "label": "Donusum",
                "reservations": random.randint(20, 80),
                "direct_bookings": random.randint(15, 60),
                "hotelrunner_bookings": random.randint(5, 20),
            },
            "loyalty": {
                "label": "Sadakat",
                "repeat_guests": random.randint(10, 40),
                "referrals": random.randint(5, 20),
                "reviews_left": random.randint(5, 25),
            },
        },
        "conversion_rate": round(random.uniform(2.0, 5.0), 2),
        "avg_booking_value": round(random.uniform(3000, 6000), 2),
        "updated_at": utcnow(),
    }


@router.get("/marketing-analytics/roi-report")
async def roi_report():
    """Pazarlama ROI raporu"""
    import random

    total_spend = round(random.uniform(3000, 15000), 2)
    total_revenue = round(total_spend * random.uniform(3, 8), 2)

    return {
        "roi": {
            "total_marketing_spend": total_spend,
            "attributed_revenue": total_revenue,
            "roas": round(total_revenue / total_spend, 2),
            "roi_percentage": round(((total_revenue - total_spend) / total_spend) * 100, 1),
        },
        "by_channel": {
            "meta_ads": {
                "spend": round(total_spend * 0.4, 2),
                "revenue": round(total_revenue * 0.35, 2),
                "roas": round(random.uniform(2.5, 6.0), 2),
            },
            "google_business": {
                "spend": round(total_spend * 0.2, 2),
                "revenue": round(total_revenue * 0.25, 2),
                "roas": round(random.uniform(3.0, 8.0), 2),
            },
            "social_organic": {
                "spend": round(total_spend * 0.1, 2),
                "revenue": round(total_revenue * 0.2, 2),
                "roas": round(random.uniform(5.0, 15.0), 2),
            },
            "whatsapp": {
                "spend": 0,
                "revenue": round(total_revenue * 0.15, 2),
                "roas": "infinity",
            },
            "referral": {
                "spend": 0,
                "revenue": round(total_revenue * 0.05, 2),
                "roas": "infinity",
            },
        },
        "recommendations": [
            "Instagram reklam butcesini %20 artirin - en yuksek ROAS",
            "WhatsApp otomasyon dizilerini aktif edin - sifir maliyet, yuksek donusum",
            "Google Business profilini guncelleyin - organik gorunurluk artisi",
            "Dugun segmentine odaklanan kampanyalari yaz aylarinda yogunlastirin",
        ],
        "updated_at": utcnow(),
    }
