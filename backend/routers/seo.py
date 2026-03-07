"""
Kozbeyli Konagi - SEO Yonetim Router
Meta tag uretimi, Schema.org, sitemap, SEO analizi, anahtar kelime onerileri
"""
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional

router = APIRouter(tags=["seo"])


class MetaTagRequest(BaseModel):
    page_type: str = "home"
    content: str = ""


class KeywordRequest(BaseModel):
    topic: str


class SEOAnalyzeRequest(BaseModel):
    content: str
    page_type: str = "general"


@router.get("/seo/schema/{schema_type}")
async def get_schema_org(schema_type: str = "Hotel"):
    """Schema.org JSON-LD structured data getir"""
    from services.seo_service import generate_schema_org
    return generate_schema_org(schema_type)


@router.get("/seo/schemas")
async def get_all_schemas():
    """Tum Schema.org tiplerini getir"""
    from services.seo_service import generate_schema_org
    types = ["Hotel", "Restaurant", "Event", "LocalBusiness"]
    return {t: generate_schema_org(t) for t in types}


@router.post("/seo/meta-tags")
async def generate_meta_tags(request: MetaTagRequest):
    """AI destekli meta tag uretimi"""
    from services.seo_service import generate_meta_tags as gen_tags
    return await gen_tags(request.page_type, request.content)


@router.get("/seo/meta-templates")
async def get_meta_templates():
    """Varsayilan meta tag sablonlarini getir"""
    from services.seo_service import DEFAULT_META_TEMPLATES
    return {"templates": DEFAULT_META_TEMPLATES}


@router.post("/seo/keywords")
async def suggest_keywords(request: KeywordRequest):
    """AI destekli anahtar kelime onerileri"""
    from services.seo_service import suggest_keywords as suggest
    return await suggest(request.topic)


@router.post("/seo/analyze")
async def analyze_seo(request: SEOAnalyzeRequest):
    """Icerik SEO skoru analizi"""
    from services.seo_service import analyze_seo_score
    return analyze_seo_score(request.content, request.page_type)


@router.get("/seo/sitemap")
async def get_sitemap():
    """XML sitemap uret"""
    from services.seo_service import generate_sitemap
    from fastapi.responses import Response
    xml = await generate_sitemap()
    return Response(content=xml, media_type="application/xml")


@router.get("/seo/local-report")
async def get_local_seo_report():
    """Yerel SEO kontrol listesi ve raporu"""
    from services.seo_service import generate_local_seo_report
    return generate_local_seo_report()
