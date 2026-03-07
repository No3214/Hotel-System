"""
Kozbeyli Konagi - Teklif Yonetimi (Proposal/Quote Management) Router
Organizasyon teklifleri olusturma, takip ve arsiv sistemi.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from database import db
from helpers import utcnow, new_id
from datetime import datetime, timezone, timedelta
from pathlib import Path
import io

router = APIRouter(tags=["proposals"])


# ===================== MODELS =====================

class AccommodationItem(BaseModel):
    room_type: str = ""
    room_count: int = 0
    nights: int = 1
    per_room_price: float = 0
    total: float = 0
    note: str = ""

class MealOption(BaseModel):
    description: str = ""
    per_person_price: float = 0
    guest_count: int = 0
    payment_method: str = ""
    total: float = 0

class ExtraService(BaseModel):
    name: str = ""
    description: str = ""
    price: float = 0

class ProposalCreate(BaseModel):
    # Musteri bilgileri
    customer_name: str
    customer_phone: str = ""
    customer_email: str = ""
    inquiry_id: str = ""
    # Etkinlik bilgileri
    event_type: str = "dugun"
    event_date: str = ""
    event_date_note: str = ""
    guest_count: int = 0
    # Konaklama
    accommodation_items: List[AccommodationItem] = []
    accommodation_total: float = 0
    accommodation_note: str = "Tum oda fiyatlarina kisi basi gurme serpme kahvalti dahildir."
    # Yemek
    meal_options: List[MealOption] = []
    meal_total: float = 0
    meal_note: str = ""
    # Ek hizmetler
    extra_services: List[ExtraService] = []
    extras_total: float = 0
    # Ozet
    grand_total: float = 0
    discount_amount: float = 0
    discount_note: str = ""
    # Odeme
    deposit_percentage: int = 50
    payment_note: str = "Kalan tutar etkinlik tarihinden 1 hafta once tahsil edilecektir."
    # Gecerlilik
    validity_days: int = 15
    # Notlar
    notes: str = ""
    internal_notes: str = ""


class AIMenuRequest(BaseModel):
    event_type: str = "dugun"
    guest_count: int = 50
    budget_per_person: float = 0
    dietary_notes: str = ""
    theme: str = ""


class ProposalUpdate(BaseModel):
    status: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    event_date: Optional[str] = None
    guest_count: Optional[int] = None
    accommodation_items: Optional[List[AccommodationItem]] = None
    accommodation_total: Optional[float] = None
    meal_options: Optional[List[MealOption]] = None
    meal_total: Optional[float] = None
    extra_services: Optional[List[ExtraService]] = None
    extras_total: Optional[float] = None
    grand_total: Optional[float] = None
    discount_amount: Optional[float] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None


# ===================== HELPER =====================

async def generate_proposal_number():
    """TKL-2026-001 formatinda teklif numarasi uret"""
    year = datetime.now(timezone.utc).year
    count = await db.proposals.count_documents({"proposal_number": {"$regex": f"TKL-{year}"}})
    return f"TKL-{year}-{str(count + 1).zfill(3)}"


# ===================== ENDPOINTS =====================

@router.post("/proposals")
async def create_proposal(data: ProposalCreate):
    """Yeni teklif olustur"""
    proposal_number = await generate_proposal_number()

    # Toplam hesapla
    acc_total = data.accommodation_total or sum(i.total for i in data.accommodation_items)
    meal_total = data.meal_total or (max((m.total for m in data.meal_options), default=0) if data.meal_options else 0)
    ext_total = data.extras_total or sum(s.price for s in data.extra_services)
    grand = data.grand_total or (acc_total + meal_total + ext_total - data.discount_amount)

    now = utcnow()
    expires = (datetime.now(timezone.utc) + timedelta(days=data.validity_days)).isoformat()

    proposal = {
        "id": new_id(),
        "proposal_number": proposal_number,
        "status": "draft",
        **data.dict(),
        "accommodation_total": acc_total,
        "meal_total": meal_total,
        "extras_total": ext_total,
        "grand_total": grand,
        "expires_at": expires,
        "sent_at": "",
        "responded_at": "",
        "created_at": now,
        "updated_at": now,
    }

    # Pydantic nesnelerini dict'e cevir
    proposal["accommodation_items"] = [i.dict() for i in data.accommodation_items]
    proposal["meal_options"] = [m.dict() for m in data.meal_options]
    proposal["extra_services"] = [s.dict() for s in data.extra_services]

    await db.proposals.insert_one(proposal)
    del proposal["_id"]

    # Inquiry varsa bagla
    if data.inquiry_id:
        await db.organization_inquiries.update_one(
            {"id": data.inquiry_id},
            {"$set": {"status": "quoted", "price_quote": grand, "proposal_id": proposal["id"], "updated_at": now}},
        )

    return proposal


@router.get("/proposals")
async def list_proposals(status: Optional[str] = None, limit: int = 100):
    """Teklifleri listele"""
    query = {}
    if status:
        query["status"] = status
    proposals = await db.proposals.find(
        query, {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    return {"proposals": proposals, "total": len(proposals)}


@router.get("/proposals/{proposal_id}")
async def get_proposal(proposal_id: str):
    """Teklif detayi"""
    p = await db.proposals.find_one({"id": proposal_id}, {"_id": 0})
    if not p:
        raise HTTPException(404, "Teklif bulunamadi")
    return p


@router.patch("/proposals/{proposal_id}")
async def update_proposal(proposal_id: str, data: ProposalUpdate):
    """Teklif guncelle"""
    update_data = {}
    for k, v in data.dict().items():
        if v is not None:
            if isinstance(v, list):
                update_data[k] = [i.dict() if hasattr(i, 'dict') else i for i in v]
            else:
                update_data[k] = v

    update_data["updated_at"] = utcnow()

    # Durum guncelleme
    if data.status == "sent":
        update_data["sent_at"] = utcnow()
    elif data.status in ("accepted", "rejected"):
        update_data["responded_at"] = utcnow()

    await db.proposals.update_one({"id": proposal_id}, {"$set": update_data})
    updated = await db.proposals.find_one({"id": proposal_id}, {"_id": 0})
    return updated


@router.delete("/proposals/{proposal_id}")
async def delete_proposal(proposal_id: str):
    """Teklif sil"""
    await db.proposals.delete_one({"id": proposal_id})
    return {"deleted": True}


@router.post("/proposals/{proposal_id}/duplicate")
async def duplicate_proposal(proposal_id: str):
    """Teklifi kopyala (yeni musteri icin sablondan olustur)"""
    original = await db.proposals.find_one({"id": proposal_id}, {"_id": 0})
    if not original:
        raise HTTPException(404, "Teklif bulunamadi")

    new_number = await generate_proposal_number()
    now = utcnow()
    expires = (datetime.now(timezone.utc) + timedelta(days=original.get("validity_days", 15))).isoformat()

    new_proposal = {
        **original,
        "id": new_id(),
        "proposal_number": new_number,
        "status": "draft",
        "customer_name": original["customer_name"] + " (Kopya)",
        "inquiry_id": "",
        "sent_at": "",
        "responded_at": "",
        "expires_at": expires,
        "created_at": now,
        "updated_at": now,
    }
    await db.proposals.insert_one(new_proposal)
    del new_proposal["_id"]
    return new_proposal


@router.get("/proposals/stats/summary")
async def proposal_stats():
    """Teklif istatistikleri"""
    total = await db.proposals.count_documents({})
    draft = await db.proposals.count_documents({"status": "draft"})
    sent = await db.proposals.count_documents({"status": "sent"})
    accepted = await db.proposals.count_documents({"status": "accepted"})
    rejected = await db.proposals.count_documents({"status": "rejected"})
    expired = await db.proposals.count_documents({"status": "expired"})

    # Toplam teklif tutari
    pipeline = [
        {"$match": {"status": {"$in": ["sent", "accepted"]}}},
        {"$group": {"_id": None, "total_value": {"$sum": "$grand_total"}, "count": {"$sum": 1}}},
    ]
    agg = await db.proposals.aggregate(pipeline).to_list(1)
    total_value = agg[0]["total_value"] if agg else 0

    # Kabul edilen toplam
    pipeline2 = [
        {"$match": {"status": "accepted"}},
        {"$group": {"_id": None, "total_value": {"$sum": "$grand_total"}}},
    ]
    agg2 = await db.proposals.aggregate(pipeline2).to_list(1)
    accepted_value = agg2[0]["total_value"] if agg2 else 0

    return {
        "total": total,
        "draft": draft,
        "sent": sent,
        "accepted": accepted,
        "rejected": rejected,
        "expired": expired,
        "total_value": total_value,
        "accepted_value": accepted_value,
        "conversion_rate": round(accepted / sent * 100, 1) if sent > 0 else 0,
    }


@router.post("/proposals/ai-menu-planner")
async def generate_ai_menu(data: AIMenuRequest):
    """Yapay Zeka destekli Banket/Etkinlik Menusu uret"""
    from gemini_service import get_chat_response
    import json
    import re

    prompt = f"""
    Sen luks ve tarihi bir mekan olan 'Kozbeyli Konagi'nin bas asisi ve etkinlik planlayacisisin.
    Amac: Asagidaki kriterlere cok uygun, detayli ve maliyetlendirilmis bir organizasyon menusu (Yemek Secenekleri) uretmek.

    Kriterler:
    - Etkinlik Turu: {data.event_type}
    - Kisi Sayisi: {data.guest_count}
    - Kisi Basi Hedef Bütce: {data.budget_per_person} TL
    - Ozel Diyet/Kisitlamalar: {data.dietary_notes}
    - Tema/Konsept: {data.theme}

    Lutfen bana bütceye uygun, yaratici ve gösterisli 1 veya 2 farkli menu opsiyonu sun.
    Sadece asagidaki JSON formatinda sonuc don. (Markdown icinde)
    [
      {{
        "description": "Orn: Vegan Ruyasi Menusu - Baslangic: ..., Ana Yemek: ..., Tatli: ...",
        "per_person_price": 450.0,
        "guest_count": {data.guest_count},
        "payment_method": "{data.theme} konseptine ozel hazirlanmistir."
      }}
    ]
    Eger bütce cok duksukse bile en iyi alternatif menuyu yarat. fiyatlar mantikli olsun.
    """

    try:
        ai_response = await get_chat_response("Menü Planla", new_id(), prompt)
        json_match = re.search(r'```(?:json)?(.*?)```', ai_response, re.DOTALL)
        res_str = json_match.group(1).strip() if json_match else ai_response
        parsed_menus = json.loads(res_str)

        for m in parsed_menus:
            m["total"] = float(m.get("per_person_price", 0)) * data.guest_count

        return {"ai_menus": parsed_menus, "analysis": "Menu, belirttiginiz butce ve konsept dahilinde AI tarafindan uretildi."}
    except Exception as e:
        return {"error": f"AI Menu uretilirken hata olustu: {str(e)}"}


# ===================== PDF GENERATION =====================

def _fmt(n):
    """Format number as Turkish currency"""
    if not n:
        return "-"
    return f"{n:,.0f} TL".replace(",", ".")


def _generate_proposal_pdf(p: dict) -> io.BytesIO:
    """Generate a professional PDF for a proposal"""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm, cm
    from reportlab.lib.colors import HexColor, black, white
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=1.5*cm, bottomMargin=2*cm, leftMargin=2*cm, rightMargin=2*cm)

    gold = HexColor("#C4972A")
    dark = HexColor("#1a1a2e")
    gray = HexColor("#666666")
    light_gold = HexColor("#FFF8E7")

    styles = getSampleStyleSheet()
    s_title = ParagraphStyle("Title2", parent=styles["Title"], fontSize=22, textColor=gold, spaceAfter=2*mm)
    s_subtitle = ParagraphStyle("Sub", parent=styles["Normal"], fontSize=10, textColor=gray, spaceAfter=4*mm)
    s_heading = ParagraphStyle("Heading", parent=styles["Heading2"], fontSize=13, textColor=dark, spaceBefore=6*mm, spaceAfter=3*mm)
    s_small = ParagraphStyle("Small", parent=styles["Normal"], fontSize=9, textColor=gray, leading=12)

    elements = []

    # --- Header with logo ---
    logo_path = Path(__file__).parent.parent / "uploads" / "logo.jpeg"
    header_data = []
    if logo_path.exists():
        img = Image(str(logo_path), width=2.2*cm, height=2.2*cm)
        header_data = [[img, Paragraph("KOZBEYLI KONAGI", ParagraphStyle("Logo", parent=styles["Title"], fontSize=20, textColor=gold, alignment=TA_LEFT))]]
    else:
        header_data = [["", Paragraph("KOZBEYLI KONAGI", ParagraphStyle("Logo", parent=styles["Title"], fontSize=20, textColor=gold, alignment=TA_LEFT))]]

    ht = Table(header_data, colWidths=[3*cm, 14*cm])
    ht.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4*mm),
    ]))
    elements.append(ht)

    # Gold line
    line_data = [["" ]]
    line_t = Table(line_data, colWidths=[17*cm], rowHeights=[1.5*mm])
    line_t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), gold)]))
    elements.append(line_t)
    elements.append(Spacer(1, 4*mm))

    # --- Proposal info ---
    elements.append(Paragraph("FIYAT TEKLIFI", s_title))
    pnum = p.get("proposal_number", "")
    created = ""
    if p.get("created_at"):
        try:
            dt = datetime.fromisoformat(p["created_at"].replace("Z", "+00:00")) if isinstance(p["created_at"], str) else p["created_at"]
            created = dt.strftime("%d.%m.%Y")
        except Exception:
            created = str(p["created_at"])[:10]
    elements.append(Paragraph(f"Teklif No: {pnum} &nbsp;&nbsp;|&nbsp;&nbsp; Tarih: {created}", s_subtitle))

    # --- Customer info ---
    elements.append(Paragraph("MUSTERI BILGILERI", s_heading))
    cust_data = [
        ["Musteri Adi:", p.get("customer_name", "-")],
        ["Telefon:", p.get("customer_phone", "-")],
    ]
    if p.get("customer_email"):
        cust_data.append(["E-posta:", p["customer_email"]])

    event_types = {"dugun": "Dugun", "nisan": "Nisan", "soz": "Soz", "kina": "Kina",
                   "dogum_gunu": "Dogum Gunu", "yil_donumu": "Yil Donumu", "kurumsal": "Kurumsal", "diger": "Diger"}
    cust_data.append(["Etkinlik Turu:", event_types.get(p.get("event_type", ""), p.get("event_type", "-"))])
    if p.get("event_date"):
        cust_data.append(["Etkinlik Tarihi:", p["event_date"]])
    if p.get("guest_count"):
        cust_data.append(["Kisi Sayisi:", str(p["guest_count"])])

    ct = Table(cust_data, colWidths=[4*cm, 13*cm])
    ct.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), gray),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2*mm),
        ("TOPPADDING", (0, 0), (-1, -1), 1*mm),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(ct)

    # --- Accommodation ---
    acc_items = [i for i in (p.get("accommodation_items") or []) if i.get("room_count", 0) > 0]
    if acc_items:
        elements.append(Paragraph("KONAKLAMA", s_heading))
        acc_data = [["Oda Tipi", "Adet", "Gece", "Birim Fiyat", "Toplam"]]
        for a in acc_items:
            total = a.get("total", 0) or (a.get("room_count", 0) * a.get("nights", 1) * a.get("per_room_price", 0))
            acc_data.append([
                a.get("room_type", "-"),
                str(a.get("room_count", 0)),
                str(a.get("nights", 1)),
                _fmt(a.get("per_room_price", 0)),
                _fmt(total),
            ])
        acc_data.append(["", "", "", "Konaklama Toplam:", _fmt(p.get("accommodation_total", 0))])

        at = Table(acc_data, colWidths=[5.5*cm, 2*cm, 2*cm, 3.5*cm, 4*cm])
        at.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), gold),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("ALIGN", (3, 0), (-1, -1), "RIGHT"),
            ("GRID", (0, 0), (-1, -2), 0.5, HexColor("#dddddd")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3*mm),
            ("TOPPADDING", (0, 0), (-1, -1), 2*mm),
            ("FONTNAME", (3, -1), (-1, -1), "Helvetica-Bold"),
            ("TEXTCOLOR", (3, -1), (-1, -1), gold),
        ]))
        elements.append(at)

        if p.get("accommodation_note"):
            elements.append(Spacer(1, 2*mm))
            elements.append(Paragraph(f"Not: {p['accommodation_note']}", s_small))

    # --- Meals ---
    meals = p.get("meal_options") or []
    if meals:
        elements.append(Paragraph("YEMEK SECENEKLERI", s_heading))
        meal_data = [["Aciklama", "Kisi Basi", "Kisi Sayisi", "Toplam"]]
        for m in meals:
            meal_data.append([
                m.get("description", "-"),
                _fmt(m.get("per_person_price", 0)),
                str(m.get("guest_count", 0)),
                _fmt(m.get("total", 0)),
            ])

        mt = Table(meal_data, colWidths=[6*cm, 3.5*cm, 3.5*cm, 4*cm])
        mt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#E67E22")),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#dddddd")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3*mm),
            ("TOPPADDING", (0, 0), (-1, -1), 2*mm),
        ]))
        elements.append(mt)

    # --- Extra Services ---
    extras = p.get("extra_services") or []
    if extras:
        elements.append(Paragraph("EK HIZMETLER", s_heading))
        ext_data = [["Hizmet", "Aciklama", "Fiyat"]]
        for e in extras:
            ext_data.append([e.get("name", "-"), e.get("description", "-"), _fmt(e.get("price", 0))])
        ext_data.append(["", "Ek Hizmetler Toplam:", _fmt(p.get("extras_total", 0))])

        et = Table(ext_data, colWidths=[4*cm, 9*cm, 4*cm])
        et.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#8E44AD")),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (2, 0), (2, -1), "RIGHT"),
            ("GRID", (0, 0), (-1, -2), 0.5, HexColor("#dddddd")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3*mm),
            ("TOPPADDING", (0, 0), (-1, -1), 2*mm),
            ("FONTNAME", (1, -1), (-1, -1), "Helvetica-Bold"),
            ("TEXTCOLOR", (1, -1), (-1, -1), HexColor("#8E44AD")),
        ]))
        elements.append(et)

    # --- Grand Total ---
    elements.append(Spacer(1, 6*mm))
    total_data = []
    if p.get("discount_amount", 0) > 0:
        total_data.append(["Indirim:", f"-{_fmt(p['discount_amount'])} {p.get('discount_note', '')}"])
    total_data.append(["GENEL TOPLAM:", _fmt(p.get("grand_total", 0))])

    if p.get("deposit_percentage"):
        deposit = (p.get("grand_total", 0) * p["deposit_percentage"]) / 100
        total_data.append([f"Kapora (%{p['deposit_percentage']}):", _fmt(deposit)])

    gt = Table(total_data, colWidths=[13*cm, 4*cm])
    gt.setStyle(TableStyle([
        ("BACKGROUND", (0, -1 if not p.get("deposit_percentage") else -2), (-1, -1 if not p.get("deposit_percentage") else -2), light_gold),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, -1 if not p.get("deposit_percentage") else -2), (-1, -1 if not p.get("deposit_percentage") else -2), 14),
        ("TEXTCOLOR", (0, -1 if not p.get("deposit_percentage") else -2), (-1, -1 if not p.get("deposit_percentage") else -2), gold),
        ("ALIGN", (0, 0), (0, -1), "RIGHT"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3*mm),
        ("TOPPADDING", (0, 0), (-1, -1), 3*mm),
    ]))
    elements.append(gt)

    # --- Payment & Notes ---
    if p.get("payment_note"):
        elements.append(Spacer(1, 4*mm))
        elements.append(Paragraph(f"Odeme Kosullari: {p['payment_note']}", s_small))

    if p.get("notes"):
        elements.append(Spacer(1, 3*mm))
        elements.append(Paragraph(f"Notlar: {p['notes']}", s_small))

    # Validity
    validity = p.get("validity_days", 15)
    elements.append(Spacer(1, 4*mm))
    elements.append(Paragraph(f"Bu teklif {validity} gun gecerlidir.", ParagraphStyle("Valid", parent=s_small, fontName="Helvetica-BoldOblique", textColor=gold)))

    # --- Footer ---
    elements.append(Spacer(1, 8*mm))
    foot_line = Table([[""]], colWidths=[17*cm], rowHeights=[1*mm])
    foot_line.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), gold)]))
    elements.append(foot_line)
    elements.append(Spacer(1, 3*mm))
    elements.append(Paragraph("Kozbeyli Konagi | Foca, Izmir | www.kozbeylikonagi.com", ParagraphStyle("Foot", parent=s_small, alignment=TA_CENTER, textColor=gold)))

    doc.build(elements)
    buf.seek(0)
    return buf


@router.get("/proposals/{proposal_id}/pdf")
async def download_proposal_pdf(proposal_id: str):
    """Teklif PDF ciktisi indir"""
    p = await db.proposals.find_one({"id": proposal_id}, {"_id": 0})
    if not p:
        raise HTTPException(404, "Teklif bulunamadi")

    buf = _generate_proposal_pdf(p)
    filename = f"{p.get('proposal_number', 'teklif')}.pdf"
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
