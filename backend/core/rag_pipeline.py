from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
import os
import shutil


class RAGPipeline:
    def __init__(self):
        self.persist_dir = "./data/chroma_db"
        os.makedirs(self.persist_dir, exist_ok=True)

        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )

        self.llm = Ollama(
            model="llama3.2:1b",
            base_url="http://localhost:11434"
        )

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=64
        )

    # 🔥 RESET (only if needed)
    def reset_db(self):
        if os.path.exists(self.persist_dir):
            shutil.rmtree(self.persist_dir)
        os.makedirs(self.persist_dir, exist_ok=True)

    # ✅ INGEST
    def ingest_documents(self, docs, collection_id):
        chunks = self.splitter.split_documents(docs)

        for chunk in chunks:
            chunk.metadata = {"source": collection_id}

        vectordb = Chroma(
            collection_name=collection_id,
            embedding_function=self.embeddings,
            persist_directory=self.persist_dir
        )

        vectordb.add_documents(chunks)
        vectordb.persist()

        return len(chunks)

    # 🧠 LLM-BASED MODE DETECTION
    def detect_mode(self, question):
        prompt = f"""
Classify the question into one of these modes:
- visual (diagrams, intuitive)
- logical (step-by-step, theory)
- story (real-world analogy)
- hybrid (mix of all)

Only return one word.

Question:
{question}
"""
        mode = self.llm.invoke(prompt).strip().lower()

        if mode not in ["visual", "logical", "story", "hybrid"]:
            return "visual"

        return mode

    # 🧠 DYNAMIC PROMPT BUILDER
    def build_prompt(self, mode, context, question, level):

        base = f"""
You are NeuralLearn AI.

Context:
{context}

Student Level: {level}

Question: {question}
"""

        if mode == "visual":
            return base + """
Explain using:
- diagrams
- bullet points
- intuitive breakdown
"""

        elif mode == "logical":
            return base + """
Explain using:
- definition
- step-by-step reasoning
- structured explanation
"""

        elif mode == "story":
            return base + """
Explain using:
- real-world analogy
- storytelling
- simple relatable examples
"""

        else:  # hybrid
            return base + """
Explain using a mix of:
- diagrams
- logical steps
- real-world analogy
Make it clear and engaging.
"""

    # ✅ QUERY (FINAL)
    def query(self, question, collection_id, level):

        mode = self.detect_mode(question)

        vectordb = Chroma(
            collection_name=collection_id,
            embedding_function=self.embeddings,
            persist_directory=self.persist_dir
        )

        retriever = vectordb.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 5}
        )

        docs = retriever.get_relevant_documents(question)

        context = "\n\n".join([doc.page_content for doc in docs])

        final_prompt = self.build_prompt(mode, context, question, level)

        response = self.llm.invoke(final_prompt)

        return {
            "answer": str(response).strip(),
            "mode_used": mode,
            "sources": [
                {
                    "preview": doc.page_content[:120],
                    "source": doc.metadata.get("source", "")
                }
                for doc in docs
            ],
            "num_sources": len(docs)
        }