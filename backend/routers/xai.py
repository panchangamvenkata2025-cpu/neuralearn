from fastapi import APIRouter
from pydantic import BaseModel
from core.xai_explainer import LevelClassifier

router = APIRouter()
model = LevelClassifier()


class XAIRequest(BaseModel):
    quiz_accuracy: float
    avg_time_per_q: float
    hint_requests: int


@router.post("/explain")
def explain(req: XAIRequest):
    try:
        features = [
            req.quiz_accuracy,
            req.avg_time_per_q,
            req.hint_requests
        ]

        result = model.explain(features)

        return result

    except Exception as e:
        return {"error": str(e)}