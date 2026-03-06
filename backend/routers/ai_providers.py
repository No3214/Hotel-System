"""
Kozbeyli Konagi - AI Provider Management Router
Multi-AI provider yonetimi ve izleme
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(tags=["ai-providers"])


class AITestRequest(BaseModel):
    message: str
    task_type: str = "general"
    preferred_provider: Optional[str] = None


class AIPromptRequest(BaseModel):
    message: str
    role: str
    task: str
    context: Optional[str] = ""
    output_format: Optional[str] = ""
    task_type: str = "general"
    preferred_provider: Optional[str] = None


@router.get("/ai/providers")
async def list_providers():
    """Kullanilabilir AI provider'lari listele"""
    from services.ai_provider_service import get_available_providers
    return {"providers": get_available_providers()}


@router.get("/ai/routing")
async def get_routing():
    """Gorev routing tablosunu goster"""
    from services.ai_provider_service import get_task_routing
    return {"routing": get_task_routing()}


@router.post("/ai/test")
async def test_ai(data: AITestRequest):
    """AI provider'i test et"""
    from services.ai_provider_service import ai_request
    result = await ai_request(
        message=data.message,
        system_prompt="Sen Kozbeyli Konagi'nin yapay zeka asistanisin. Turkce cevap ver.",
        task_type=data.task_type,
        preferred_provider=data.preferred_provider,
    )
    return result


@router.post("/ai/smart-request")
async def smart_request(data: AIPromptRequest):
    """Akilli AI istegi - best practice prompt ile"""
    from services.ai_provider_service import ai_request, build_system_prompt

    system_prompt = build_system_prompt(
        role=data.role,
        task=data.task,
        context=data.context or "",
        output_format=data.output_format or "",
    )

    result = await ai_request(
        message=data.message,
        system_prompt=system_prompt,
        task_type=data.task_type,
        preferred_provider=data.preferred_provider,
    )
    return result


# ==================== MARKETING REPORTS ====================

@router.get("/ai/marketing-reports")
async def get_marketing_reports(limit: int = 10, report_type: Optional[str] = None):
    """Pazarlama raporlarini ve itibar uyarilarini listele"""
    from database import db
    query = {}
    if report_type:
        query["type"] = report_type
    reports = await db.marketing_reports.find(
        query, {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    return {"reports": reports, "total": len(reports)}


@router.get("/ai/marketing-reports/latest")
async def get_latest_report():
    """Son gunluk pazarlama raporunu getir"""
    from database import db
    report = await db.marketing_reports.find_one(
        {"type": "daily_marketing_report"}, {"_id": 0},
        sort=[("created_at", -1)]
    )
    alerts = await db.marketing_reports.find(
        {"type": "reputation_alert"}, {"_id": 0}
    ).sort("created_at", -1).limit(5).to_list(5)
    return {"report": report, "recent_alerts": alerts}


@router.get("/ai/usage-stats")
async def get_usage_stats(days: int = 30):
    """AI kullanim istatistiklerini getir"""
    from services.ai_provider_service import get_ai_usage_stats
    stats = await get_ai_usage_stats(days)
    return stats
