VISUAL_SIGNALS  = ["show", "diagram", "look", "picture", "see", "visualize", "draw", "map", "chart", "graph"]
LOGICAL_SIGNALS = ["prove", "formula", "equation", "derive", "calculate", "formal", "steps", "algorithm"]
STORY_SIGNALS   = ["analogy", "story", "explain like", "example", "real world", "imagine", "metaphor"]


class CognitiveEngine:
    def __init__(self):
        self.history = []  # stores previous queries

    def detect_mode(self, query: str) -> dict:
        try:
            # ✅ ensure input is string (prevents your previous error)
            if not isinstance(query, str):
                query = str(query)

            # ✅ add to history
            self.history.append(query)

            # ✅ keep only last 5 queries (sliding window)
            recent_queries = self.history[-5:]

            scores = {"visual": 0, "logical": 0, "story": 0}

            for q in recent_queries:
                if not isinstance(q, str):
                    continue

                q = q.lower()

                scores["visual"]  += sum(s in q for s in VISUAL_SIGNALS)
                scores["logical"] += sum(s in q for s in LOGICAL_SIGNALS)
                scores["story"]   += sum(s in q for s in STORY_SIGNALS)

            total = sum(scores.values())

            # ✅ fallback if no signals detected
            if total == 0:
                return {
                    "mode": "visual",
                    "confidence": 0.5,
                    "scores": {
                        "visual": 0.33,
                        "logical": 0.33,
                        "story": 0.33
                    }
                }

            # ✅ pick highest scoring mode
            mode = max(scores, key=scores.get)
            confidence = scores[mode] / total

            return {
                "mode": mode,
                "confidence": round(confidence, 2),
                "scores": {
                    k: round(v / total, 2) for k, v in scores.items()
                }
            }

        except Exception as e:
            # ✅ safe fallback (never crash backend)
            return {
                "mode": "visual",
                "confidence": 0.5,
                "scores": {
                    "visual": 0.33,
                    "logical": 0.33,
                    "story": 0.33
                },
                "error": str(e)
            }