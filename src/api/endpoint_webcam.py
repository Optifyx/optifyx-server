from fastapi import APIRouter
from fastapi.responses import StreamingResponse, JSONResponse
import cv2
import io

router = APIRouter()

@router.get("/webcam_check")
async def webcam_check():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return JSONResponse(
            status_code=200,
            content={"message": "Webcam not available"},
        )
    
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return JSONResponse(
            status_code=200,
            content={"message": "Failed to capture image from webcam"},
        )

    _, img_encoded = cv2.imencode('.webp', frame)
    img_bytes = img_encoded.tobytes()
    return StreamingResponse(io.BytesIO(img_bytes), media_type="image/webp")
