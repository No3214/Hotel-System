from fastapi import APIRouter, HTTPException
from typing import Optional
from database import db
from helpers import utcnow, new_id, clean_doc
from hotel_data import HOTEL_INFO, HOTEL_AWARDS, HOTEL_POLICIES, HOTEL_HISTORY, FOCA_LOCAL_GUIDE, ROOMS

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
