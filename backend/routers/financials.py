"""
Gelir/Gider Takip Modulu - Kozbeyli Konagi
Income/Expense CRUD, daily/monthly reports, KPI, commission reports.
"""
from fastapi import APIRouter, Query, Request, HTTPException
from typing import Optional
from datetime import date, datetime, timedelta, timezone
from database import db
from helpers import utcnow, new_id
import calendar

router = APIRouter(tags=["financials"])

TOTAL_ROOMS = 16

INCOME_CATEGORIES = [
    {"key": "room", "label": "Oda Geliri"},
    {"key": "restaurant", "label": "Restoran"},
    {"key": "bar", "label": "Bar"},
    {"key": "event", "label": "Etkinlik"},
    {"key": "minibar", "label": "Minibar"},
    {"key": "extra_service", "label": "Ekstra Hizmet"},
    {"key": "other", "label": "Diger"},
]

EXPENSE_CATEGORIES = [
    {"key": "food_supplies", "label": "Gida Malzemesi"},
    {"key": "beverages", "label": "Icecek"},
    {"key": "cleaning", "label": "Temizlik Malzemesi"},
    {"key": "energy", "label": "Elektrik/Su/Dogalgaz"},
    {"key": "salary", "label": "Maas"},
    {"key": "insurance", "label": "Sigorta"},
    {"key": "maintenance", "label": "Bakim/Onarim"},
    {"key": "marketing", "label": "Pazarlama"},
    {"key": "commission", "label": "OTA Komisyon"},
    {"key": "tax", "label": "Vergi"},
    {"key": "rent", "label": "Kira"},
    {"key": "equipment", "label": "Ekipman"},
    {"key": "laundry", "label": "Camasir"},
    {"key": "garden", "label": "Bahce Bakimi"},
    {"key": "entertainment", "label": "Eglence/Sanatci"},
    {"key": "software", "label": "Yazilim/Teknoloji"},
    {"key": "other", "label": "Diger"},
]


# ==================== CATEGORIES ====================

@router.get("/financials/categories")
async def get_categories():
    return {
        "income_categories": INCOME_CATEGORIES,
        "expense_categories": EXPENSE_CATEGORIES,
    }


# ==================== INCOME CRUD ====================

@router.post("/financials/income")
async def add_income(request: Request):
    body = await request.json()
    record = {
        "id": new_id(),
        "type": "income",
        "date": body.get("date", date.today().isoformat()),
        "category": body.get("category", "other"),
        "description": body.get("description", ""),
        "amount": float(body.get("amount", 0)),
        "source": body.get("source", "direct"),
        "reservation_id": body.get("reservation_id"),
        "commission_rate": float(body.get("commission_rate", 0)),
        "created_at": utcnow(),
    }

    # Calculate net amount after commission
    if record["commission_rate"] > 0:
        record["commission_amount"] = round(record["amount"] * record["commission_rate"] / 100, 2)
        record["net_amount"] = round(record["amount"] - record["commission_amount"], 2)
    else:
        record["commission_amount"] = 0
        record["net_amount"] = record["amount"]

    await db.financials.insert_one(record)
    return {"success": True, "id": record["id"], "message": "Gelir kaydedildi"}


@router.get("/financials/income")
async def list_income(
    date_from: Optional[str] = Query(default=None),
    date_to: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    limit: int = Query(default=100),
):
    query = {"type": "income"}
    if date_from:
        query["date"] = {"$gte": date_from}
    if date_to:
        query.setdefault("date", {})["$lte"] = date_to
    if category:
        query["category"] = category

    records = await db.financials.find(query, {"_id": 0}).sort("date", -1).limit(limit).to_list(limit)
    return {"records": records, "total": len(records)}


# ==================== EXPENSE CRUD ====================

@router.post("/financials/expense")
async def add_expense(request: Request):
    body = await request.json()
    record = {
        "id": new_id(),
        "type": "expense",
        "date": body.get("date", date.today().isoformat()),
        "category": body.get("category", "other"),
        "description": body.get("description", ""),
        "amount": float(body.get("amount", 0)),
        "is_paid": body.get("is_paid", True),
        "vendor": body.get("vendor", ""),
        "created_at": utcnow(),
    }
    await db.financials.insert_one(record)
    return {"success": True, "id": record["id"], "message": "Gider kaydedildi"}


@router.get("/financials/expense")
async def list_expenses(
    date_from: Optional[str] = Query(default=None),
    date_to: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    limit: int = Query(default=100),
):
    query = {"type": "expense"}
    if date_from:
        query["date"] = {"$gte": date_from}
    if date_to:
        query.setdefault("date", {})["$lte"] = date_to
    if category:
        query["category"] = category

    records = await db.financials.find(query, {"_id": 0}).sort("date", -1).limit(limit).to_list(limit)
    return {"records": records, "total": len(records)}


# ==================== DELETE ====================

@router.delete("/financials/{record_id}")
async def delete_financial_record(record_id: str):
    result = await db.financials.delete_one({"id": record_id})
    if result.deleted_count == 0:
        return {"success": False, "error": "Kayit bulunamadi"}
    return {"success": True, "message": "Kayit silindi"}


# ==================== DAILY SUMMARY ====================

@router.get("/financials/daily/{date_str}")
async def daily_summary(date_str: str):
    incomes = await db.financials.find(
        {"type": "income", "date": date_str}, {"_id": 0}
    ).to_list(500)
    expenses = await db.financials.find(
        {"type": "expense", "date": date_str}, {"_id": 0}
    ).to_list(500)

    total_income = sum(r.get("net_amount", r.get("amount", 0)) for r in incomes)
    total_expense = sum(r.get("amount", 0) for r in expenses)

    # Group by category
    income_by_cat = {}
    for r in incomes:
        cat = r.get("category", "other")
        income_by_cat[cat] = income_by_cat.get(cat, 0) + r.get("net_amount", r.get("amount", 0))

    expense_by_cat = {}
    for r in expenses:
        cat = r.get("category", "other")
        expense_by_cat[cat] = expense_by_cat.get(cat, 0) + r.get("amount", 0)

    return {
        "date": date_str,
        "income": {"total": round(total_income, 2), "by_category": income_by_cat, "count": len(incomes)},
        "expense": {"total": round(total_expense, 2), "by_category": expense_by_cat, "count": len(expenses)},
        "profit": round(total_income - total_expense, 2),
    }


# ==================== MONTHLY SUMMARY ====================

@router.get("/financials/monthly")
async def monthly_summary(
    year: int = Query(default=None),
    month: int = Query(default=None),
):
    if not year:
        year = date.today().year
    if not month:
        month = date.today().month

    days_in_month = calendar.monthrange(year, month)[1]
    date_from = f"{year}-{month:02d}-01"
    date_to = f"{year}-{month:02d}-{days_in_month}"

    incomes = await db.financials.find(
        {"type": "income", "date": {"$gte": date_from, "$lte": date_to}}, {"_id": 0}
    ).to_list(5000)
    expenses = await db.financials.find(
        {"type": "expense", "date": {"$gte": date_from, "$lte": date_to}}, {"_id": 0}
    ).to_list(5000)

    total_income = sum(r.get("net_amount", r.get("amount", 0)) for r in incomes)
    total_expense = sum(r.get("amount", 0) for r in expenses)
    gross_income = sum(r.get("amount", 0) for r in incomes)
    total_commission = sum(r.get("commission_amount", 0) for r in incomes)

    # Group by category
    income_by_cat = {}
    for r in incomes:
        cat = r.get("category", "other")
        income_by_cat[cat] = income_by_cat.get(cat, 0) + r.get("net_amount", r.get("amount", 0))

    expense_by_cat = {}
    for r in expenses:
        cat = r.get("category", "other")
        expense_by_cat[cat] = expense_by_cat.get(cat, 0) + r.get("amount", 0)

    # Source breakdown
    income_by_source = {}
    for r in incomes:
        src = r.get("source", "direct")
        if src not in income_by_source:
            income_by_source[src] = {"gross": 0, "commission": 0, "net": 0, "count": 0}
        income_by_source[src]["gross"] += r.get("amount", 0)
        income_by_source[src]["commission"] += r.get("commission_amount", 0)
        income_by_source[src]["net"] += r.get("net_amount", r.get("amount", 0))
        income_by_source[src]["count"] += 1

    # Daily trend
    daily_trend = []
    for day in range(1, days_in_month + 1):
        d = f"{year}-{month:02d}-{day:02d}"
        day_income = sum(r.get("net_amount", r.get("amount", 0)) for r in incomes if r.get("date") == d)
        day_expense = sum(r.get("amount", 0) for r in expenses if r.get("date") == d)
        daily_trend.append({"date": d, "income": round(day_income, 2), "expense": round(day_expense, 2)})

    # KPI
    reservations = await db.reservations.find({
        "check_in": {"$gte": date_from, "$lte": date_to},
        "status": {"$in": ["confirmed", "checked_in", "checked_out"]},
    }, {"_id": 0, "total_price": 1, "check_in": 1, "check_out": 1}).to_list(5000)

    occupied_nights = 0
    for r in reservations:
        try:
            ci = datetime.strptime(r.get("check_in", ""), "%Y-%m-%d")
            co = datetime.strptime(r.get("check_out", ""), "%Y-%m-%d")
            occupied_nights += max(0, (co - ci).days)
        except (ValueError, TypeError):
            pass

    total_room_nights = TOTAL_ROOMS * days_in_month
    occupancy = round(occupied_nights / total_room_nights * 100, 1) if total_room_nights > 0 else 0
    adr = round(total_income / occupied_nights) if occupied_nights > 0 else 0
    revpar = round(total_income / total_room_nights) if total_room_nights > 0 else 0
    profit_margin = round((total_income - total_expense) / total_income * 100, 1) if total_income > 0 else 0

    return {
        "period": f"{year}-{month:02d}",
        "income": {
            "gross": round(gross_income, 2),
            "net": round(total_income, 2),
            "commission": round(total_commission, 2),
            "by_category": income_by_cat,
            "by_source": income_by_source,
            "count": len(incomes),
        },
        "expense": {
            "total": round(total_expense, 2),
            "by_category": expense_by_cat,
            "count": len(expenses),
        },
        "profit": round(total_income - total_expense, 2),
        "profit_margin": profit_margin,
        "daily_trend": daily_trend,
        "kpis": {
            "occupancy_rate": occupancy,
            "adr": adr,
            "revpar": revpar,
            "total_reservations": len(reservations),
            "occupied_nights": occupied_nights,
            "total_room_nights": total_room_nights,
        },
    }


# ==================== AI AUDIT (PHASE 9) ====================

@router.get("/financials/ai-audit")
async def get_financial_audit(
    year: int = Query(default=None),
    month: int = Query(default=None),
):
    try:
        from gemini_service import get_chat_response
        import json
        
        if not year:
            year = date.today().year
        if not month:
            month = date.today().month

        days_in_month = calendar.monthrange(year, month)[1]
        date_from = f"{year}-{month:02d}-01"
        date_to = f"{year}-{month:02d}-{days_in_month}"

        # Get records for the month to analyze
        incomes = await db.financials.find(
            {"type": "income", "date": {"$gte": date_from, "$lte": date_to}}, {"_id": 0}
        ).to_list(500)
        expenses = await db.financials.find(
            {"type": "expense", "date": {"$gte": date_from, "$lte": date_to}}, {"_id": 0}
        ).to_list(500)
        
        # We need a clean summary of expenses and vendors for the prompt
        expense_summary = []
        for e in expenses:
            expense_summary.append({
                "date": e.get("date"),
                "category": e.get("category"),
                "vendor": e.get("vendor", "Bilinmiyor"),
                "amount": e.get("amount", 0),
                "description": e.get("description", "")
            })
            
        income_summary = []
        for i in incomes:
            income_summary.append({
                "date": i.get("date"),
                "category": i.get("category"),
                "source": i.get("source", "Bilinmiyor"),
                "amount": i.get("amount", 0)
            })

        prompt = f"""
        Sen Kozbeyli Konagi'nin yapay zeka CFO'susun (Finansal Denetci).
        Asagida {year}-{month} donemine ait gelir ve gider kayitlari verilmistir.
        Bu verileri cok detayli inceleyip bana profesyonel ve derinlemesine bir denetim raporu cikarmani istiyorum.
        
        Senden beklenenler:
        1. "Finansal Saglik Skoru (financial_score)": 0 ile 100 arasinda bir puan ver. (100 = Mukemmel).
        2. "Anomaliler ve Riskler (anomalies)": Dikkat ceken orantisiz gider tutarlari, mukerrer (ayni gun ayni tutar) basilmis kayitlar veya eksik/hatali gozuken islemler.
        3. "Tasarruf ve Tedarikci ROI (savings_recommendations)": Tedarikcilere ucan paralari veya kategorisel asimlari analiz et, alternatif yontemlerle nasil tasarruf edebilecegimizi 'impact' degeri (high/medium/low) ile listele.
        4. "Gelir Artirma Stratejileri (revenue_insights)": Gelir kalemlerine (kanallara ve kategorilere) bakarak nerelerde daha yuksek komisyon odendigini veya hangi servisten daha fazla para kazanabilecegimizi gosteren spesifik satıs taktikleri. (Orn: 'Oda servisi satisiniz cok dusuk', 'Booking komisyonlari cok yuksek, direkt satisa yonelin').
        5. "Genel CFO Ozeti (summary)": Yonetim kuruluna sunulacak formatta, rakamsal analizler iceren yonetici ozeti.
        
        Gider Kayitlari:
        {json.dumps(expense_summary, ensure_ascii=False, indent=2)[:3500]}
        ...
        
        Gelir Kayitlari Ozet:
        {json.dumps(income_summary, ensure_ascii=False, indent=2)[:2000]}
        ...
        
        Lutfen SADECE asagidaki JSON formatinda cevap don:
        {{
          "financial_score": 85,
          "summary": "Bu ayki mali tablolarda %X kar marji gozlemlendi...",
          "anomalies": [
             {{"type": "Mukerrer Kayit Riski", "description": "X firmasina ayni gun icinde 2 kez odeme basilmis.", "severity": "high"}}
          ],
          "savings_recommendations": [
             {{"title": "Enerji Tasarrufu Piki", "detail": "Elektrik gideriniz beklentinin cok uzerinde...", "impact": "high"}}
          ],
          "revenue_insights": [
             {{"title": "OTA Komisyon Uyarisi", "detail": "Booking.com'dan gelen rezervasyon komisyonlari %20'yi gecti, CTA kampanyalari yapilmali."}}
          ]
        }}
        """
        
        ai_resp = await get_chat_response("financials", new_id(), prompt)
        
        import re
        json_match = re.search(r'```(?:json)?(.*?)```', ai_resp, re.DOTALL)
        res_str = json_match.group(1).strip() if json_match else ai_resp
        audit_data = json.loads(res_str)
        
        return {
            "success": True,
            "period": f"{year}-{month:02d}",
            "audit": audit_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Denetim hesaplanamadi: {str(e)}")

# ==================== PHASE 16: AI FINANCIAL FORECAST ====================

@router.get("/financials/ai-forecast")
async def get_financial_forecast():
    """
    Son 3 aylik harcama ve gelir trendlerine, ayni zamanda gelecek rezervasyonlara bakarak 
    onumuzdeki ayki net nakit akisi, elektrik faturasi vb. tahminlerini ve tavsiyeleri uretir.
    """
    try:
        from gemini_service import get_chat_response
        import json
        
        # Son 3 ayin verilerini topla
        today = date.today()
        three_months_ago = (today.replace(day=1) - timedelta(days=90)).isoformat()
        
        incomes = await db.financials.find(
            {"type": "income", "date": {"$gte": three_months_ago}}, 
            {"_id": 0, "date": 1, "category": 1, "net_amount": 1, "amount": 1}
        ).to_list(1000)
        
        expenses = await db.financials.find(
            {"type": "expense", "date": {"$gte": three_months_ago}}, 
            {"_id": 0, "date": 1, "category": 1, "amount": 1}
        ).to_list(1000)

        # Gelecek ay rezervasyonlari (doluluk gostergesi)
        next_month_start = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
        next_month_end = (next_month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        
        future_res = await db.reservations.find({
            "check_in": {"$gte": next_month_start.isoformat(), "$lte": next_month_end.isoformat()},
            "status": {"$in": ["confirmed", "pending"]}
        }).to_list(100)
        
        future_kpi = f"Gelecek ay {len(future_res)} adet teyitli/bekleyen rezervasyon var."

        # Veriyi kucult (Prompt limitini asmamak icin ay bazinda toplamlari al)
        monthly_summary_data = {}
        for i in incomes:
            m = i["date"][:7] # YYYY-MM
            if m not in monthly_summary_data: monthly_summary_data[m] = {"inc": 0, "exp": 0}
            monthly_summary_data[m]["inc"] += i.get("net_amount", i.get("amount", 0))
            
        for e in expenses:
            m = e["date"][:7]
            if m not in monthly_summary_data: monthly_summary_data[m] = {"inc": 0, "exp": 0}
            monthly_summary_data[m]["exp"] += e.get("amount", 0)

        prompt = f"""
        Sen Kozbeyli Konagi'nin AI Finansal Tahmincisi'sin (Forecast/Projeksiyon).
        Otelimizin son 3 aylik gelir/gider ozeti su sekilde:
        {json.dumps(monthly_summary_data, indent=2)}
        
        Ayrica gelecek ayki rezervasyon durumu: {future_kpi}
        
        Mevcut enflasyonist ortami, otelcilik sezon trendlerini ve veriyi baz alarak gelecek ay icin mantikli, sayisal bir finansal tahmin raporu cikar.
        
        SADECE asagidaki JSON formatinda sonuc ver:
        {{
          "projected_revenue_try": 120000,
          "projected_expense_try": 80000,
          "projected_profit_try": 40000,
          "expected_occupancy_percent": 65,
          "forecast_notes": [
            "Gecen aya gore elektrik maliyetlerinde %15 artis ongoruluyor.",
            "Gelecek ayki rezervasyon hizina bakilarak oda geliri sabit kalacaktir."
          ],
          "actionable_advice": [
            "Klima bakimlarini erkenden yaptirarak enerji artisini frenleyin."
          ]
        }}
        """
        
        ai_resp = await get_chat_response("financials_forecast", new_id(), prompt)
        
        import re
        json_match = re.search(r'```(?:json)?(.*?)```', ai_resp, re.DOTALL)
        res_str = json_match.group(1).strip() if json_match else ai_resp
        forecast_data = json.loads(res_str)
        
        return {
            "success": True,
            "period": next_month_start.strftime("%Y-%m"),
            "forecast": forecast_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Forecast hesaplanamadi: {str(e)}")

# ==================== PHASE 23: AI VENDOR ROI & PROCUREMENT ANALYTICS ====================

@router.get("/financials/ai-vendor-roi")
async def get_vendor_roi_analysis(months_back: int = 6):
    """
    Tedarikci bazinda kâr/zarar ve enflasyon analizi yapar. 
    Son aylardaki fiyat artislarini, anomalileri tespit eder ve anlik tasarruf raporu sunar.
    """
    try:
        from gemini_service import get_chat_response
        import json
        from collections import defaultdict
        
        # Son X ayin verilerini topla
        today = date.today()
        start_date = (today.replace(day=1) - timedelta(days=30 * months_back)).isoformat()
        
        expenses = await db.financials.find(
            {"type": "expense", "date": {"$gte": start_date}}, 
            {"_id": 0, "date": 1, "category": 1, "amount": 1, "vendor": 1, "description": 1}
        ).to_list(2000)

        if not expenses:
            return {"success": False, "message": "Yeterli gider verisi bulunamadi."}

        # Veriyi tedarikci bazinda grupla (AI'in daha iyi anlamasi icin)
        # Format: vendor_summary["Kasap Veli"]["2026-01"] = toplam_tutar
        vendor_data = defaultdict(lambda: defaultdict(float))
        vendor_categories = defaultdict(set)
        
        for e in expenses:
            vendor = e.get("vendor", "").strip() or "Diger/Bilinmeyen"
            month = e["date"][:7] # YYYY-MM
            amount = e.get("amount", 0)
            cat = e.get("category", "other")
            
            vendor_data[vendor][month] += amount
            vendor_categories[vendor].add(cat)

        # Prompt icin formati hazirla
        analysis_payload = {}
        for vendor, months in vendor_data.items():
            # Sadece toplam hacmi belli bir uzerinde olanlari (veya tumunu) analize gonder
            analysis_payload[vendor] = {
                "categories": list(vendor_categories[vendor]),
                "monthly_spending": dict(months)
            }

        prompt = f"""
        Sen oteller zincirinin 'Yapay Zeka CFO'su ve Satin Alma Muduru'sun.
        Gorevin, otelimizin son {months_back} aylik tedarikci (vendor) harcamalarini inceleyip bize kesin, rakamsal ve sarsici bir geri donus (ROI) ve maliyet analizi sunmak.
        
        Asagida tedarikcilerimize ay bazinda yaptigimiz harcama (TRY) ve alisveris kategorileri bulunuyor:
        {json.dumps(analysis_payload, ensure_ascii=False, indent=2)[:6000]}
        
        Senden beklenenler:
        1. "Genel Satin Alma Durumu (procurement_health_score)": 0-100 arasi puan ver.
        2. "Kirmizi Bayraklar (red_flags)": Gecen aylara gore sebepsiz/asiri fiyat artisi (enflasyon ustu sisme) yapan tedarikcileri tespit et.
        3. "Tasarruf Firsatlari (savings_opportunities)": Hangi tedarikciyi degistirirsek veya hangi alimlari toptan yaparsak ne kadar tasarruf edecegimizi (Aylik kac TL) rakamsal olarak belirt.
        4. "Tedarikci Performans Ozeti (vendor_insights)": En cok para harcadigimiz ilk 3 tedarikcinin analizini yapip bize birer cumlelik yonetici notu dus (Devam et/Pazarlik yap/Degistir).
        
        Lutfen SADECE asagidaki JSON formatinda cevap don, markdown block icinde de olsa sadece asagidaki yapiyi koru:
        {{
          "procurement_health_score": 75,
          "summary_message": "Tedarik zinciriniz genel olarak istikrarli ancak gida tedarikcilerinde %20'lik aciklanamayan maliyet artisi var...",
          "red_flags": [
            {{"vendor": "Manav Ali", "issue": "Aylik harcama egrisi son 2 ayda %45 firlamis. Fiyat sismesi olabilir.", "severity": "high"}}
          ],
          "savings_opportunities": [
            {{"opportunity": "Temizlik Malzemesi Toptan Alimi", "estimated_monthly_saving_try": 5000, "action": "X firmasindan aylik almak yerine 3 aylik toptan anlasma yapin."}}
          ],
          "vendor_insights": [
             {{"vendor": "Kasap Veli", "status": "renegotiate", "note": "Giderler stabil degil, birim fiyatlar icin masaya oturun."}}
          ]
        }}
        """
        
        ai_resp = await get_chat_response("financials_vendor_roi", new_id(), prompt)
        
        import re
        json_match = re.search(r'```(?:json)?(.*?)```', ai_resp, re.DOTALL)
        res_str = json_match.group(1).strip() if json_match else ai_resp
        report_data = json.loads(res_str)
        
        return {
            "success": True,
            "period": f"Son {months_back} Ay",
            "report": report_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI CFO Tedarikci Analizi yapilamadi: {str(e)}")

