from fastapi import APIRouter, HTTPException
from src.core.gps import detect_gps_device
from src.core.internet import get_public_ip
from src.core.metrics import request_counts
import psutil

router = APIRouter()

@router.get("/security_realtime")
async def get_security_realtime():
    try:
        gps_data = detect_gps_device()
        if not gps_data:
            gps_data = get_public_ip()
        battery = psutil.sensors_battery()
        return {
            "battery": f"{battery.percent}%" if battery else "Not Available",
            "location": gps_data,
            "requests_success": request_counts["requests_success"],
            "requests_malformed": request_counts["requests_malformed"],
            "requests_bad": request_counts["requests_bad"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))