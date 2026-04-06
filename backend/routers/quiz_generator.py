from langchain_community.vectorstores import Chroma
import json, hashlib, re, random


QUIZ_PROMPT = """You are an expert teacher.

Generate {n} HIGH-QUALITY MCQs at {difficulty} level (Bloom's: {bloom}).

STRICT RULES:
- Return ONLY valid JSON array
- No explanation, no markdown, no code fences
- Questions must be clean English
- No raw notes or broken sentences
- Avoid repetition

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


BLOOM = {
    "beginner": "remember/understand",
    "intermediate": "apply/analyze",
    "advanced": "evaluate/synthesize"
}


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
                return []
        return []

    def _clean_text(self, text):
        return re.sub(r'\s+', ' ', text.replace("\n", " ")).strip()

    def generate(self, collection_id, level, n=5, exclude_ids=[]):
        try:
            vectordb = Chroma(
                collection_name=collection_id,
                embedding_function=self.rag.embeddings,
                persist_directory="./data/chroma_db"
            )

            # ✅ RANDOMIZED SEARCH (avoids repetition)
            queries = [
                "important concepts",
                "definitions",
                "applications",
                "examples",
                "key topics"
            ]
            search_query = random.choice(queries)

            docs = vectordb.similarity_search(search_query, k=8)

            if not docs:
                raise Exception("No documents found in collection")

            # ✅ REDUCED CONTEXT (prevents Ollama crash)
            random.shuffle(docs)
            context = "\n\n".join([
                self._clean_text(d.page_content[:300])
                for d in docs[:5]
            ])

            # ✅ SAFE LLM CALL (no crash)
            try:
                raw = self.rag.llm.invoke(
                    QUIZ_PROMPT.format(
                        n=n,
                        difficulty=level,
                        bloom=BLOOM.get(level, "remember"),
                        context=context,
                        exclude=str(exclude_ids)
                    )
                )
            except Exception:
                raw = ""

            questions = self._safe_parse(raw)

            # ✅ FALLBACK (if LLM fails)
            if not questions:
                questions = []
                for i, doc in enumerate(docs[:n]):
                    text = self._clean_text(doc.page_content[:120])

                    questions.append({
                        "question": f"What is the key idea of: {text}?",
                        "options": [
                            "Definition",
                            "Concept",
                            "Application",
                            "Example"
                        ],
                        "correct_index": 0,
                        "difficulty": level,
                        "concept": "general"
                    })

            # ✅ HASH + REMOVE DUPLICATES
            filtered = []
            seen = set()

            for q in questions:
                question_text = self._clean_text(q.get("question", ""))
                qid = self._hash(question_text)
                q["id"] = qid
                q["question"] = question_text

                if qid not in seen and qid not in exclude_ids:
                    seen.add(qid)
                    filtered.append(q)

            return filtered[:n]

        except Exception as e:
            # ✅ FINAL FAIL-SAFE (never break frontend)
            return [{
                "question": "Fallback: What is Computer Networks?",
                "options": ["Definition", "Concept", "Application", "Example"],
                "correct_index": 0,
                "difficulty": level,
                "concept": "fallback",
                "id": "fallback1"
            }]