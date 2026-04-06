import numpy as np
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine

class DriftDetector:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.DRIFT_THRESHOLD = 0.35
        self.session_embeddings = []

    def check_drift(self, new_query: str, session_queries: list[str]) -> dict:
        new_emb = self.model.encode(new_query)

        if len(session_queries) < 2:
            self.session_embeddings.append(new_emb)
            return {"drift_score": 0.0, "is_drifting": False}

        # Compute centroid of session embeddings
        centroid = np.mean(self.session_embeddings, axis=0)
        drift_score = float(cosine(new_emb, centroid))

        self.session_embeddings.append(new_emb)
        is_drifting = drift_score > self.DRIFT_THRESHOLD

        return {
            "drift_score": round(drift_score, 3),
            "is_drifting": is_drifting,
            "action": "inject_micro_quiz" if is_drifting else "continue",
            "message": ("⚓ Anchoring back to core topic..." if is_drifting else "On track")
        }