from fastapi import APIRouter
from pydantic import BaseModel
from core.rag_pipeline import RAGPipeline
from core.cognitive_engine import CognitiveEngine
from core.drift_detector import DriftDetector

router = APIRouter()

rag = RAGPipeline()
engine = CognitiveEngine()
drift = DriftDetector()

# store session history
SESSION_HISTORY = []


class ChatRequest(BaseModel):
    question: str
    collection_id: str
    level: str


@router.post("/")
def chat(req: ChatRequest):
    try:
        # 1. Track history
        SESSION_HISTORY.append(req.question)

        # 2. Cognitive mode detection (ONLY for analytics)
        mode_info = engine.detect_mode(req.question)

        # 3. Drift detection
        drift_info = drift.check_drift(
            new_query=req.question,
            session_queries=SESSION_HISTORY
        )

        # 4. If drifting → interrupt
        if drift_info["is_drifting"]:
            return {
                "message": "You seem distracted. Quick check:",
                "quiz": {
                    "question": "What was the main topic we were discussing?",
                    "type": "short_answer"
                },
                "drift_info": drift_info
            }

        # 5. RAG (🔥 NO cognitive_mode here)
        result = rag.query(
            question=req.question,
            collection_id=req.collection_id,
            level=req.level
        )

        return {
            "answer": result["answer"],
            "mode_used": result["mode_used"],  # from RAG (LLM-based)
            "mode_info": mode_info,            # from cognitive engine
            "drift_info": drift_info,
            "sources": result["sources"]
        }

    except Exception as e:
        return {"error": str(e)}
        
        
        

    