from fastapi import APIRouter, HTTPException
from src.core.hardware import get_system_realtime, get_disk_realtime

router = APIRouter()

@router.get("/system_realtime")
async def system_realtime():
    try:
        return get_system_realtime()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/disk_realtime")
async def disk_realtime():
    try:
        return get_disk_realtime()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))