from langchain_community.vectorstores import Chroma
import json
import hashlib
import re
import random


# =========================
# 🔥 IMPROVED PROMPT
# =========================
QUIZ_PROMPT = """
You are an expert teacher.

Generate {n} HIGH-QUALITY MCQs at {difficulty} level
(Bloom's: {bloom}) from the content below.

RULES:
- Return ONLY valid JSON array
- No explanation, no markdown
- Questions must be clean and meaningful
- DO NOT include raw text, code, or broken sentences
- Avoid repetition
- Each question must test understanding

Avoid these question hashes: {exclude}

Content:
{context}

FORMAT:
[
  {{
    "question": "Clear question",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_index": 0,
    "difficulty": "{difficulty}",
    "concept": "topic"
  }}
]
"""


# =========================
# BLOOM LEVELS
# =========================
BLOOM = {
    "beginner": "remember/understand",
    "intermediate": "apply/analyze",
    "advanced": "evaluate/synthesize"
}


# =========================
# GENERATOR CLASS
# =========================
class QuizGenerator:

    def __init__(self, rag):
        self.rag = rag

    def _hash(self, text):
        return hashlib.md5(text.encode()).hexdigest()[:8]

    def _safe_parse(self, raw):
        try:
            return json.loads(raw)
        except:
            try:
                match = re.search(r'\[.*\]', raw, re.DOTALL)
                if match:
                    return json.loads(match.group())
            except:
                pass
        return []

    # =========================
    # 🔥 MAIN FUNCTION
    # =========================
    def generate(self, collection_id, level, n=5, exclude_ids=[]):
        try:
            vectordb = Chroma(
                collection_name=collection_id,
                embedding_function=self.rag.embeddings,
                persist_directory="./data/chroma_db"
            )

            # 🔥 RANDOMIZED RETRIEVAL (FIXES SAME QUESTIONS)
            queries = [
                "important concepts",
                "definitions",
                "applications",
                "examples",
                "key topics",
                "numericals",
                "theory explanation"
            ]

            search_query = random.choice(queries)

            docs = vectordb.similarity_search(search_query, k=8)

            context = "\n\n".join([d.page_content for d in docs])[:3000]

            # =========================
            # 🔥 LLM CALL
            # =========================
            raw = self.rag.llm.invoke(
                QUIZ_PROMPT.format(
                    n=n,
                    difficulty=level,
                    bloom=BLOOM.get(level, "remember"),
                    context=context,
                    exclude=str(exclude_ids)
                )
            )

            questions = self._safe_parse(raw)

            # =========================
            # 🔥 CLEAN + FILTER
            # =========================
            cleaned = []

            for q in questions:
                if "question" not in q or "options" not in q:
                    continue

                qid = self._hash(q["question"])
                q["id"] = qid

                # remove duplicates
                if qid in exclude_ids:
                    continue

                # basic cleaning
                q["question"] = q["question"].replace("\n", " ").strip()

                cleaned.append(q)

            # =========================
            # 🔥 FALLBACK (CLEAN VERSION)
            # =========================
            if not cleaned:
                for i, doc in enumerate(docs[:n]):
                    text = doc.page_content.strip().replace("\n", " ")

                    question_text = f"What is the key concept explained in: {text[:100]}?"

                    qid = self._hash(question_text)

                    if qid in exclude_ids:
                        continue

                    cleaned.append({
                        "question": question_text,
                        "options": [
                            "Definition",
                            "Concept",
                            "Application",
                            "Example"
                        ],
                        "correct_index": 1,
                        "difficulty": level,
                        "concept": "general",
                        "id": qid
                    })

            return cleaned[:n]

        except Exception as e:
            raise Exception(f"QuizGenerator Error: {str(e)}")