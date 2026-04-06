from fastapi import APIRouter, UploadFile, File
import os
import shutil
from core.file_processor import extract_text_from_file
from core.rag_pipeline import RAGPipeline

router = APIRouter()

UPLOAD_DIR = "backend/data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

rag = RAGPipeline()


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract text
        documents = extract_text_from_file(file_path)

        # Create unique collection id
        collection_id = file.filename.replace(".", "_")

        # Store in vector DB
        chunk_count = rag.ingest_documents(documents, collection_id)

        return {
            "message": "File uploaded & processed successfully",
            "collection_id": collection_id,
            "chunks": chunk_count
        }

    except Exception as e:
        return {"error": str(e)}