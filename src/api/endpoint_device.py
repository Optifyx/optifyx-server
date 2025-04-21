from fastapi import APIRouter, Request, HTTPException
from src.core.code import generate_code, generated_code, display_code_window
from src.models.code_request import CodeRequest
import threading

router = APIRouter()

@router.post("/start_device")
async def start_device():
    try:
        global generated_code
        generated_code = generate_code()
        threading.Thread(target=display_code_window, args=(generated_code,)).start()
        return {"message": "Device started! A code is displayed on the screen."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/connection_code")
async def connection_code(request: Request, data: CodeRequest):
    try:
        if data.code == generated_code:
            return {"message": "Connection authorized!"}
        else:
            raise HTTPException(status_code=400, detail="Invalid code!")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))