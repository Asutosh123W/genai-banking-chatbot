from backend.services.vector_store import retrieve_relevant_chunks
from backend.services.llm_service import generate_response
from backend.services.vector_store import store_chunks
from backend.services.document_processor import (
    extract_text_from_pdf,
    extract_text_from_txt,
    chunk_text
)
from fastapi import APIRouter, UploadFile, File
from backend.models.chat_models import ChatRequest
import os

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "Backend running successfully"}


@router.post("/chat")
def chat(request: ChatRequest):

    retrieved_chunks = retrieve_relevant_chunks(request.message)

    ai_response = generate_response(
        request.message,
        retrieved_chunks
    )

    return {
        "question": request.message,
        "response": ai_response
    }


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    upload_dir = "backend/data/uploads"

    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # Extract text
    if file.filename.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)

    elif file.filename.endswith(".txt"):
        text = extract_text_from_txt(file_path)

    else:
        return {"error": "Unsupported file format"}

    # Chunk text
    chunks = chunk_text(text)

    # Store in vector DB
    store_chunks(chunks, file.filename)

    return {
        "filename": file.filename,
        "total_characters": len(text),
        "total_chunks": len(chunks),
        "sample_chunk": chunks[0] if chunks else "No chunks created",
        "message": "Document processed successfully"
    }