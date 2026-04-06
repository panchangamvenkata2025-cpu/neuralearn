from fastapi import APIRouter
from pydantic import BaseModel
import base64
import numpy as np
import cv2
import threading
from core.attention_tracker import AttentionTracker

router = APIRouter()
tracker = AttentionTracker()


class FrameRequest(BaseModel):
    image_base64: str


@router.post("/score")
def get_attention_score(req: FrameRequest):
    try:
        image_bytes = base64.b64decode(req.image_base64)

        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        result = tracker.analyze(frame)

        return result

    except Exception as e:
        return {"error": str(e)}


@router.get("/start-camera")
def start_camera():
    try:
        threading.Thread(target=tracker.start).start()
        return {"message": "Camera started"}
    except Exception as e:
        return {"error": str(e)}
        
        
