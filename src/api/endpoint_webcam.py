from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import cv2
import io

router = APIRouter()

@router.get("/webcam_check")
async def webcam_check():
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise HTTPException(status_code=500, detail="Unable to access the webcam")
        ret, frame = cap.read()
        cap.release()
        if not ret:
            raise HTTPException(status_code=500, detail="Failed to capture image")
        _, img_encoded = cv2.imencode('.webp', frame)
        img_bytes = img_encoded.tobytes()
        return StreamingResponse(io.BytesIO(img_bytes), media_type="image/webp")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))