"""
Kozbeyli Konagi - Mutfak Dashboard Router
Siparis yonetimi, hazirlik durumu, bildirimler
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, List
from database import db
from helpers import utcnow, new_id, clean_doc
from pydantic import BaseModel
from enum import Enum
from datetime import datetime, timedelta, timezone

router = APIRouter(tags=["kitchen"])


class OrderStatus(str, Enum):
    pending = "pending"           # Bekliyor
    preparing = "preparing"       # Hazirlaniyor
    ready = "ready"               # Hazir
    served = "served"             # Servis Edildi
    cancelled = "cancelled"       # Iptal


class OrderType(str, Enum):
    room_service = "room_service"  # Oda servisi
    restaurant = "restaurant"      # Restoran
    event = "event"                # Etkinlik
    takeaway = "takeaway"          # Paket


class OrderItem(BaseModel):
    name: str
    quantity: int
    notes: Optional[str] = None
    price: Optional[float] = None


class CreateOrderRequest(BaseModel):
    order_type: OrderType
    items: List[OrderItem]
    table_number: Optional[int] = None
    room_number: Optional[str] = None
    guest_name: Optional[str] = None
    special_notes: Optional[str] = None
    priority: Optional[str] = "normal"  # low, normal, high, urgent


class UpdateOrderStatusRequest(BaseModel):
    status: OrderStatus
    notes: Optional[str] = None


# Siparis Olustur
@router.post("/kitchen/orders")
async def create_order(data: CreateOrderRequest):
    order = {
        "id": new_id(),
        "order_type": data.order_type,
        "items": [item.model_dump() for item in data.items],
        "table_number": data.table_number,
        "room_number": data.room_number,
        "guest_name": data.guest_name,
        "special_notes": data.special_notes,
        "priority": data.priority,
        "status": OrderStatus.pending,
        "total_items": sum(item.quantity for item in data.items),
        "created_at": utcnow(),
        "updated_at": utcnow(),
        "status_history": [
            {"status": OrderStatus.pending, "timestamp": utcnow(), "notes": "Siparis alindi"}
        ],
    }
    await db.kitchen_orders.insert_one(order)
    return clean_doc(order)


# Siparisleri Listele
@router.get("/kitchen/orders")
async def list_orders(
    status: Optional[str] = None,
    order_type: Optional[str] = None,
    date: Optional[str] = None,
    limit: int = 50
):
    query = {}
    
    if status:
        if status == "active":
            query["status"] = {"$in": [OrderStatus.pending, OrderStatus.preparing]}
        else:
            query["status"] = status
    
    if order_type:
        query["order_type"] = order_type
    
    if date:
        try:
            target_date = datetime.fromisoformat(date)
            start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
            query["created_at"] = {"$gte": start.isoformat(), "$lt": end.isoformat()}
        except Exception:
            pass
    
    orders = await db.kitchen_orders.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    
    # Istatistikler
    stats = {
        "pending": await db.kitchen_orders.count_documents({"status": OrderStatus.pending}),
        "preparing": await db.kitchen_orders.count_documents({"status": OrderStatus.preparing}),
        "ready": await db.kitchen_orders.count_documents({"status": OrderStatus.ready}),
        "today_total": await db.kitchen_orders.count_documents({
            "created_at": {"$gte": datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()}
        }),
    }
    
    return {"orders": orders, "stats": stats, "total": len(orders)}


# Siparis Detay
@router.get("/kitchen/orders/{order_id}")
async def get_order(order_id: str):
    order = await db.kitchen_orders.find_one({"id": order_id}, {"_id": 0})
    if not order:
        raise HTTPException(404, "Siparis bulunamadi")
    return order


# Siparis Durumu Guncelle
@router.put("/kitchen/orders/{order_id}/status")
async def update_order_status(order_id: str, data: UpdateOrderStatusRequest):
    order = await db.kitchen_orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(404, "Siparis bulunamadi")
    
    history_entry = {
        "status": data.status,
        "timestamp": utcnow(),
        "notes": data.notes or f"Durum guncellendi: {data.status}",
    }
    
    await db.kitchen_orders.update_one(
        {"id": order_id},
        {
            "$set": {
                "status": data.status,
                "updated_at": utcnow(),
            },
            "$push": {"status_history": history_entry}
        }
    )
    
    updated = await db.kitchen_orders.find_one({"id": order_id}, {"_id": 0})
    return clean_doc(updated)


# Siparis Iptal
@router.delete("/kitchen/orders/{order_id}")
async def cancel_order(order_id: str):
    order = await db.kitchen_orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(404, "Siparis bulunamadi")
    
    await db.kitchen_orders.update_one(
        {"id": order_id},
        {
            "$set": {
                "status": OrderStatus.cancelled,
                "updated_at": utcnow(),
            },
            "$push": {"status_history": {
                "status": OrderStatus.cancelled,
                "timestamp": utcnow(),
                "notes": "Siparis iptal edildi"
            }}
        }
    )
    return {"success": True}


# Gunluk Ozet
@router.get("/kitchen/summary")
async def get_daily_summary():
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    
    pipeline = [
        {"$match": {"created_at": {"$gte": today_start}}},
        {"$group": {
            "_id": "$status",
            "count": {"$sum": 1},
            "total_items": {"$sum": "$total_items"}
        }}
    ]
    
    result = await db.kitchen_orders.aggregate(pipeline).to_list(10)
    
    summary = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "by_status": {r["_id"]: {"count": r["count"], "items": r["total_items"]} for r in result},
        "total_orders": sum(r["count"] for r in result),
        "total_items": sum(r["total_items"] for r in result),
    }
    
    # En cok siparis edilen urunler
    item_pipeline = [
        {"$match": {"created_at": {"$gte": today_start}}},
        {"$unwind": "$items"},
        {"$group": {
            "_id": "$items.name",
            "count": {"$sum": "$items.quantity"}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    
    top_items = await db.kitchen_orders.aggregate(item_pipeline).to_list(10)
    summary["top_items"] = [{"name": i["_id"], "count": i["count"]} for i in top_items]
    
    return summary


# Mutfak Bildirimleri
@router.get("/kitchen/notifications")
async def get_notifications():
    # Acil ve yuksek oncelikli bekleyen siparisler
    urgent_orders = await db.kitchen_orders.find(
        {"status": OrderStatus.pending, "priority": {"$in": ["high", "urgent"]}},
        {"_id": 0}
    ).sort("created_at", 1).to_list(10)
    
    # 15 dakikadan fazla bekleyen siparisler
    fifteen_min_ago = (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
    delayed_orders = await db.kitchen_orders.find(
        {"status": OrderStatus.pending, "created_at": {"$lt": fifteen_min_ago}},
        {"_id": 0}
    ).to_list(10)
    
    return {
        "urgent": urgent_orders,
        "delayed": delayed_orders,
        "urgent_count": len(urgent_orders),
        "delayed_count": len(delayed_orders),
    }
