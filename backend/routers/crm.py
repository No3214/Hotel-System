from fastapi import APIRouter, Query, Request, HTTPException
from typing import Optional
from database import db
from helpers import utcnow, new_id

router = APIRouter(tags=["crm"])

# ----------------- CRM CORE -----------------

@router.get("/crm/deals")
async def get_deals():
    """Tum CRM adaylarini/firsatlarini getirir."""
    deals = await db.crm_deals.find({}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return {"deals": deals}

@router.post("/crm/deals")
async def create_deal(request: Request):
    """Yeni bir sirket/firsat ekler."""
    body = await request.json()
    deal_id = new_id()
    
    deal = {
        "id": deal_id,
        "company_name": body.get("company_name", "Bilinmeyen Sirket"),
        "contact_person": body.get("contact_person", ""),
        "email": body.get("email", ""),
        "phone": body.get("phone", ""),
        "sector": body.get("sector", "Diger"),
        "status": body.get("status", "lead"), # lead, contacted, proposal, won, lost
        "estimated_value": float(body.get("estimated_value", 0)),
        "notes": body.get("notes", ""),
        "created_at": utcnow(),
        "updated_at": utcnow()
    }
    await db.crm_deals.insert_one(deal)
    return {"success": True, "id": deal_id, "deal": deal}

@router.put("/crm/deals/{deal_id}/status")
async def update_deal_status(deal_id: str, request: Request):
    """Asama (Status) guncellemesi yapar (Kanban surukle-birak icin)"""
    body = await request.json()
    new_status = body.get("status")
    if not new_status:
         raise HTTPException(status_code=400, detail="Eksik parametre")
         
    res = await db.crm_deals.update_one(
        {"id": deal_id}, 
        {"$set": {"status": new_status, "updated_at": utcnow()}}
    )
    if res.modified_count == 0:
        return {"success": False, "message": "Firsat bulunamadi veya ayni."}
    return {"success": True}

@router.delete("/crm/deals/{deal_id}")
async def delete_deal(deal_id: str):
    await db.crm_deals.delete_one({"id": deal_id})
    return {"success": True}

# ----------------- AI B2B FEATURES -----------------

@router.post("/crm/ai-lead-discovery")
async def simulate_ai_lead_discovery():
    """
    Bolgedeki (Aliağa, Menemen, Foca vb. cevre sanayi) potansiyel sirketleri analiz edip
    sisteme yeni 'lead'ler olarak ekler.
    """
    try:
        from gemini_service import get_chat_response
        import json
        
        prompt = """
        Sen Kozbeyli Konagi'nin (Luks butik otel) B2B Satis Direktoru AI'isin.
        Otel Aliaga, Menemen ve Foca bolgesine hitap etmektedir.
        Bu bolgelerde genellikle ruzgar enerjisi firmalari, petrokimya ve lojistik firmalari, serbest bolge sirketleri bulunur.
        Bana tamamen hayal urunu ama cok gercekci duran 3 sirket uretmeni istiyorum. Bu sirketler 
        otelde muhendislerini, yabanci denetcilerini veya stajyerlerini agirliyabilecek profilde olmali.
        
        SADECE asagidaki JSON array formatinda ciktilar uret:
        [
          {
            "company_name": "Aegean Wind Turbines",
            "contact_person": "Cem Yilmaz (IK Muduru)",
            "email": "cem.yilmaz@aegeanwind.com",
            "phone": "+90 555 123 4567",
            "sector": "Rüzgar Enerjisi",
            "estimated_value": 150000,
            "notes": "Hollanda'dan gelen muhendislerin uzun donem konaklamasi icin uygun aday."
          }
        ]
        """
        
        ai_resp = await get_chat_response("crm_ai_leads", new_id(), prompt)
        
        import re
        json_match = re.search(r'```(?:json)?(.*?)```', ai_resp, re.DOTALL)
        res_str = json_match.group(1).strip() if json_match else ai_resp
        leads = json.loads(res_str)
        
        inserted_deals = []
        for l in leads:
            deal_id = new_id()
            deal = {
                "id": deal_id,
                "company_name": l.get("company_name", "Yeni Sirket"),
                "contact_person": l.get("contact_person", ""),
                "email": l.get("email", ""),
                "phone": l.get("phone", ""),
                "sector": l.get("sector", "Endustri"),
                "status": "lead", # Hepsi yeni aday
                "estimated_value": float(l.get("estimated_value", 50000)),
                "notes": l.get("notes", "Yapay zeka tarafindan potansiyel müşteri olarak kesfedildi."),
                "created_at": utcnow(),
                "updated_at": utcnow()
            }
            await db.crm_deals.insert_one(deal)
            inserted_deals.append(deal)
            
        return {"success": True, "deals": inserted_deals}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Lead Kesfi basarisiz oldu: {str(e)}")


@router.get("/crm/deals/{deal_id}/ai-pitch")
async def generate_sales_pitch(deal_id: str):
    """
    Belirtilen CRM firsatinin (sirketin) sektorune ve notlarina bakarak, 
    onlara e-posta ile atilabilecek/gonderilebilecek cok kaliteli bir teklif metni (pitch) olusturur.
    """
    deal = await db.crm_deals.find_one({"id": deal_id})
    if not deal:
        raise HTTPException(status_code=404, detail="Firsat (Deal) bulunamadi.")
        
    try:
        from gemini_service import get_chat_response
        
        prompt = f"""
        Sen Kozbeyli Konagi luks butik otelinin kurumsal satis mudurusun.
        Asagidaki sirketin yetkilisi olan '{deal.get("contact_person")}' ismine bir isbirligi/teklif maili (sales pitch) yazacaksin.
        Bu mail B2B satisa yonelik olmali, profesyonel ayni zamanda cok cekici bir dille yazilmali.
        
        Sirket Bilgileri:
        - Sirket Adi: {deal.get("company_name")}
        - Sektor: {deal.get("sector")}
        - Ek Bilgi/Not: {deal.get("notes")}
        - Beklenen Olası Ciro (Tahmini Müşteri Değeri): {deal.get("estimated_value")} TL ciro beklentimiz var.
        
        Bu firmaya ozel (ornegin lojistikse kaptanlara, enerji ise muhendislere ozel oldugunu hissettiren) 
        Neden bizi (Kozbeyli Konagi'ni) kurumsal konaklamalarinda tercih etmeleri gerektigini (ornegin sanayiye cok yakin ama bir o kadar da stresten uzak luks bir konak tarzinda olmamizi) 
        anlatan bir Kurumsal Konaklama Anlasmasi teklifi e-postasi yaz.
        
        Mailde 'Özel Kurumsal Fiyat Anlaşması' (Corporate Rate Agreement) sunacagini belirt.
        Yazi Markdown formatinda sik bir sekilde basilmali, Subject/Konu basligini da ayrica icersin. Lutfen SADECE mail metnini dondur (aciklama yapma).
        """
        
        ai_resp = await get_chat_response("crm_sales_pitch", deal_id, prompt)
        
        return {"success": True, "pitch": ai_resp.strip()}
        
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Satise Yonelik Pitch hazirlanamadi: {str(e)}")
