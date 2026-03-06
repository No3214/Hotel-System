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
