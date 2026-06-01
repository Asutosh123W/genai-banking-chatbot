from fastapi import Depends

from fastapi.responses import StreamingResponse

from sqlalchemy.orm import Session

from backend.database.database import (
    get_db
)

from backend.services.token_service import (
    get_current_email
)

from backend.services.user_service import (
    get_user_by_email
)

from backend.services.vector_store import (
    retrieve_relevant_chunks,
    store_chunks,
    get_documents,
    delete_document,
    get_collection_stats,
    get_collection
)

from backend.services.llm_service import (
    generate_response,
    stream_response
)
from backend.services.session_service import (
    create_session,
    get_user_sessions,
    delete_session,
    get_session_messages,
    save_message,
    update_session_title,
    get_recent_messages
)

from backend.services.document_processor import (
    extract_text_from_pdf,
    extract_text_from_txt,
    chunk_text
)

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form
)

from backend.models.session_models import (
    RenameSessionRequest
)

from backend.models.chat_models import (
    ChatRequest
)
from backend.database.models import ChatSession

import os

router = APIRouter()


@router.get("/health")
def health_check():

    return {
        "status": "Backend running successfully"
    }


@router.get("/documents/{knowledge_base}")
def list_documents(
    knowledge_base: str,
    email: str = Depends(
        get_current_email
    ),
    db: Session = Depends(
        get_db
    )
):

    user = get_user_by_email(
        email,
        db
    )

    if not user:

        return {
            "message":
            "Unauthorized user"
        }

    documents = get_documents(
        user.id,
        knowledge_base
    )

    return {
        "knowledge_base":
            knowledge_base,
        "total_documents":
            len(documents),
        "documents":
            documents
    }

@router.get(
    "/stats/{knowledge_base}"
)
def get_stats(
    knowledge_base: str,
    email: str = Depends(
        get_current_email
    ),
    db: Session = Depends(
        get_db
    )
):

    user = get_user_by_email(
        email,
        db
    )

    if not user:

        return {
            "message":
            "Unauthorized user"
        }

    return get_collection_stats(
        user.id,
        knowledge_base
    )

@router.delete(
    "/documents/{knowledge_base}/{filename}"
)
def remove_document(
    knowledge_base: str,
    filename: str,
    email: str = Depends(
        get_current_email
    ),
    db: Session = Depends(
        get_db
    )
):

    user = get_user_by_email(
        email,
        db
    )

    if not user:

        return {
            "message":
            "Unauthorized user"
        }

    deleted_chunks = delete_document(
        filename,
        user.id,
        knowledge_base
    )

    file_path = os.path.join(
        "backend/data/uploads",
        filename
    )

    if os.path.exists(file_path):

        os.remove(file_path)

    return {

        "message":
            "Document deleted",

        "filename":
            filename,

        "deleted_chunks":
            deleted_chunks
    }

    file_path = os.path.join(
        "backend/data/uploads",
        filename
    )

    if os.path.exists(file_path):

        os.remove(file_path)

    return {

        "message":
            "Document deleted",

        "filename":
            filename,

        "deleted_chunks":
            deleted_chunks
    }

@router.post("/sessions")
def create_chat_session(
    email: str = Depends(
        get_current_email
    ),
    db: Session = Depends(
        get_db
    )
):

    user = get_user_by_email(
        email,
        db
    )

    if not user:

        return {
            "message":
            "Unauthorized user"
        }

    session = create_session(
        user_id=user.id,
        db=db
    )

    return {
        "id": session.id,
        "title": session.title
    }

@router.get("/sessions")
def list_chat_sessions(
    email: str = Depends(
        get_current_email
    ),
    db: Session = Depends(
        get_db
    )
):
    print("EMAIL FROM TOKEN:", email)

    user = get_user_by_email(
        email,
        db
    )

    print("USER FOUND:", user)

    if not user:

        return {
            "message":
            "Unauthorized user"
        }

    sessions = get_user_sessions(
        user.id,
        db
    )

    return [

        {
            "id": session.id,
            "title": session.title
        }

        for session in sessions
    ]

@router.get(
    "/sessions/{session_id}/messages"
)
def get_messages(
    session_id: int,
    email: str = Depends(
        get_current_email
    ),
    db: Session = Depends(
        get_db
    )
):

    user = get_user_by_email(
        email,
        db
    )

    if not user:

        return {
            "message":
            "Unauthorized user"
        }

    messages = get_session_messages(
        session_id,
        user.id,
        db
    )

    return [

        {
            "id": message.id,
            "sender": message.sender,
            "content": message.content,
            "sources": message.sources
        }

        for message in messages
    ]

@router.delete(
    "/sessions/{session_id}"
)
def remove_session(
    session_id: int,
    email: str = Depends(
        get_current_email
    ),
    db: Session = Depends(
        get_db
    )
):

    user = get_user_by_email(
        email,
        db
    )

    if not user:

        return {
            "message":
            "Unauthorized user"
        }

    success = delete_session(
        session_id,
        user.id,
        db
    )

    return {
        "success": success
    }

@router.put(
    "/sessions/{session_id}"
)
def rename_session(

    session_id: int,

    request:
    RenameSessionRequest,

    email: str = Depends(
        get_current_email
    ),

    db: Session = Depends(
        get_db
    )

):

    user = get_user_by_email(
        email,
        db
    )

    if not user:

        return {
            "message":
            "Unauthorized user"
        }

    session = (
        db.query(ChatSession)
        .filter(
            ChatSession.id ==
            session_id,

            ChatSession.user_id ==
            user.id
        )
        .first()
    )

    if not session:

        return {
            "message":
            "Session not found"
        }

    session.title = (
        request.title
    )

    db.commit()

    return {
        "message":
        "Session renamed"
    }


@router.post("/chat")
def chat(
    request: ChatRequest,
    email: str = Depends(
        get_current_email
    ),
    db: Session = Depends(
        get_db
    )
):

    user = get_user_by_email(
        email,
        db
    )

    if not user:

        return {
            "message":
            "Unauthorized user"
        }

    session = (
        db.query(ChatSession)
        .filter(
            ChatSession.id == request.session_id,
            ChatSession.user_id == user.id
        )
        .first()
    )

    if not session:

        return {
            "message":
            "Invalid session"
        }

    # AUTO TITLE GENERATION
    if session.title == "New Chat":

        update_session_title(
            session_id=session.id,
            title=request.message[:40],
            db=db
        )

    save_message(
        session_id=request.session_id,
        sender="user",
        content=request.message,
        sources="",
        db=db
    )

    retrieved_chunks, metadata = (
        retrieve_relevant_chunks(
            query=request.message,
            user_id=user.id,
            collection_name=request.knowledge_base
        )
    )

    history_messages = get_recent_messages(
    session_id=request.session_id,
    limit=6,
    db=db
)

    ai_response = generate_response(
        request.message,
        retrieved_chunks,
        history_messages
    )

    sources = list(
        set(
            item["source"]
            for item in metadata
        )
    )

    save_message(
        session_id=request.session_id,
        sender="bot",
        content=ai_response,
        sources=", ".join(sources),
        db=db
    )

    return {
        "question":
            request.message,
        "knowledge_base":
            request.knowledge_base,
        "response":
            ai_response,
        "sources":
            sources
    }


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    knowledge_base: str = Form("general"),
    email: str = Depends(
        get_current_email
    ),
    db: Session = Depends(
        get_db
    )
):

    upload_dir = "backend/data/uploads"

    os.makedirs(
        upload_dir,
        exist_ok=True
    )

    file_path = os.path.join(
        upload_dir,
        file.filename
    )

    with open(file_path, "wb") as buffer:

        content = await file.read()

        buffer.write(content)

        print("EMAIL:", email)
    
    user = get_user_by_email(
        email,
        db
    )

    if not user:

     return {
        "message":
        "Unauthorized user"
    }

    # PDF

    if file.filename.endswith(".pdf"):

        text = extract_text_from_pdf(
            file_path
        )

    # TXT

    elif file.filename.endswith(".txt"):

        text = extract_text_from_txt(
            file_path
        )

    else:

        return {
            "error":
                "Unsupported file format"
        }

    chunks = chunk_text(text)

    print("TOTAL CHUNKS:", len(chunks))

    print(
        "FIRST CHUNK:",
        chunks[0][:200]
    )

    print("EMAIL:", email)
    print("USER OBJECT:", user)
    print("USER ID:", user.id)

    store_chunks(
    chunks=chunks,
    filename=file.filename,
    user_id=user.id,
    collection_name=knowledge_base
)

    return {
        "filename":
            file.filename,
        "knowledge_base":
            knowledge_base,
        "total_characters":
            len(text),
        "total_chunks":
            len(chunks),
        "sample_chunk":
            chunks[0]
            if chunks
            else "No chunks created",
        "message":
            "Document processed successfully"
    }

@router.get("/debug-documents/{knowledge_base}")
def debug_documents(
    knowledge_base: str
):

    collection = get_collection(
        knowledge_base
    )

    results = collection.get()

    return {
        "count": len(results["metadatas"]),
        "metadatas": results["metadatas"][:10]
    }

@router.post("/chat-stream")
def chat_stream(
    request: ChatRequest,
    email: str = Depends(
        get_current_email
    ),
    db: Session = Depends(
        get_db
    )
):

    user = get_user_by_email(
        email,
        db
    )

    if not user:

        return {
            "message":
            "Unauthorized user"
        }

    session = (
        db.query(ChatSession)
        .filter(
            ChatSession.id == request.session_id,
            ChatSession.user_id == user.id
        )
        .first()
    )

    if not session:

        return {
            "message":
            "Invalid session"
        }

    # Auto-title first message
    if session.title == "New Chat":

        update_session_title(
            session_id=session.id,
            title=request.message[:40],
            db=db
        )

    # Save user message
    save_message(
        session_id=request.session_id,
        sender="user",
        content=request.message,
        sources="",
        db=db
    )

    retrieved_chunks, metadata = (
        retrieve_relevant_chunks(
            query=request.message,
            user_id=user.id,
            collection_name=request.knowledge_base
        )
    )

    history_messages = get_recent_messages(
    session_id=request.session_id,
    limit=6,
    db=db
)

    sources = list(
        set(
            item["source"]
            for item in metadata
        )
    )

    def generate():

        full_response = ""

        for token in stream_response(
            request.message,
            retrieved_chunks,
            history_messages
        ):

            full_response += token

            yield token

        save_message(
            session_id=request.session_id,
            sender="bot",
            content=full_response,
            sources=", ".join(sources),
            db=db
        )

    return StreamingResponse(
        generate(),
        media_type="text/plain"
    )