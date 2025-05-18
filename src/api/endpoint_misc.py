from fastapi import APIRouter, HTTPException
import socket
from src.core.internet import get_public_ip

router = APIRouter()

@router.get("/public_ip")
async def public_ip():
    try:
        return get_public_ip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/check_online_connections")
async def check_online_connections():
    try:
        device_name = socket.gethostname()
        return {
            "status": "Online",
            "device_name": device_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))