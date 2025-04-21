from fastapi import APIRouter, HTTPException
from src.core.hardware import get_home_realtime

router = APIRouter()

@router.get("/home_realtime")
async def home_realtime():
    try:
        return get_home_realtime()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))