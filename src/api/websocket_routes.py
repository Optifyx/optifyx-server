from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
from src.core.hardware import get_home_realtime, get_system_realtime, get_disk_realtime
from src.api.endpoint_security import get_security_realtime

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        while True:
            data = await websocket.receive_text()
            if data == "/home_realtime":
                response = get_home_realtime()
            elif data == "/system_realtime":
                response = get_system_realtime()
            elif data == "/disk_realtime":
                response = get_disk_realtime()
            elif data == "/security_realtime":
                response = get_security_realtime()
            else:
                response = {"error": "Invalid command"}
            await websocket.send_text(json.dumps(response))
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_text(json.dumps({"error": str(e)}))