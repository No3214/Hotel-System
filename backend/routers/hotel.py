from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import db
from helpers import utcnow, new_id, clean_doc
from hotel_data import HOTEL_INFO, HOTEL_AWARDS, HOTEL_POLICIES, HOTEL_HISTORY, FOCA_LOCAL_GUIDE, ROOMS

class ItineraryRequest(BaseModel):
    guest_type: str = "cift"
    days: int = 2
    interests: str = "Tarih, lezzet, dinlenme"

router = APIRouter(tags=["hotel"])


@router.get("/hotel/info")
async def get_hotel_info():
    return HOTEL_INFO


@router.get("/hotel/awards")
async def get_hotel_awards():
    return {"awards": HOTEL_AWARDS}


@router.get("/hotel/policies")
async def get_hotel_policies():
    return HOTEL_POLICIES


@router.get("/hotel/history")
async def get_hotel_history():
    return HOTEL_HISTORY


@router.get("/hotel/guide")
async def get_local_guide():
    return FOCA_LOCAL_GUIDE

@router.post("/hotel/guide/ai-itinerary")
async def generate_ai_itinerary(data: ItineraryRequest):
    """Misafirin profiline gore dinamik AI Foça rotasi cikarir"""
    from gemini_service import get_chat_response
    import json
    import re

    prompt = f"""
    Sen Kozbeyli Konagi'nin (Foça, Izmir) uzman yerel rehberi, nam-i diger AI Konsiyerjsin.
    Misafir profili sunlar:
    - Misafir Tipi: {data.guest_type} (orn: Aile, Tek kisi, Cift, Arkadas grubu)
    - Konaklama Suresi: {data.days} Gun
    - Ilgi Alanlari: {data.interests}

    Senden lutfen bu misafire ozel {data.days} gunluk detayli, saat saat bir seyahat rotasi cikarmani istiyorum.
    Kozbeyli Koyu'nden baslayarak Foça'nin tarihi yerlerini, plajlarini ve en iyi restoranlarini (Antakya Sofrasi dahil) icermelidir.

    Lutfen SADECE asagidaki JSON formatinda sonuc don. Kod blogu disinda yazi yazma.
    {{
      "title": "{data.days} Gunluk Harika Foca Rotaniz",
      "summary": "Bu rotanin amaci, misafire hitap eden kisa on yazi...",
      "itinerary": [
        {{
          "day": 1,
          "activities": [
            {{"time": "09:00", "title": "Kozbeyli'de Geleneksel Kahvalti", "description": "Kozbeyli Konagi'nin bahcesinde organik serpme kahvalti."}},
            {{"time": "11:30", "title": "Foca Antik Liman Gezisi", "description": "Eski Foca sokaklarinda yurumek ve Phokaia kazilarini gormek."}}
          ]
        }}
      ]
    }}
    """
    try:
        ai_response = await get_chat_response("Konsiyerj Rota", new_id(), prompt)
        json_match = re.search(r'```(?:json)?(.*?)```', ai_response, re.DOTALL)
        res_str = json_match.group(1).strip() if json_match else ai_response
        parsed_itinerary = json.loads(res_str)

        return {"success": True, "data": parsed_itinerary}
    except Exception as e:
        return {"error": f"AI Rota uretilirken hata olustu: {str(e)}"}
