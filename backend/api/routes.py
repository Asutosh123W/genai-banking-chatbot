from fastapi import Depends

from fastapi.responses import StreamingResponse

from sqlalchemy.orm import Session

from database.database import (
    get_db
)
from database.models import (
    EvaluationMetric
)

from services.token_service import (
    get_current_email
)

from services.user_service import (
    get_user_by_email
)

from services.evaluation_db_service import (
    save_evaluation_metric
)

from services.agent_service import (
    choose_tool,
    plan_tools,
    compare_documents,
    generate_document_report,
    synthesize_tool_results,
    match_job_requirements
)
from services.document_summary_service import (
    summarize_documents
)

from services.evaluation_service import (
    calculate_answer_relevancy,
    calculate_faithfulness,
    calculate_context_precision
)

from services.vector_store import (
    retrieve_relevant_chunks,
    store_chunks,
    get_documents,
    delete_document,
    get_collection_stats,
    get_collection,
    retrieve_multi_query_chunks
)

from services.llm_service import (
    generate_response,
    stream_response,
    rewrite_query,
    generate_search_queries
)
from services.session_service import (
    create_session,
    get_user_sessions,
    delete_session,
    get_session_messages,
    save_message,
    update_session_title,
    get_recent_messages
)

from services.document_processor import (
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

from models.session_models import (
    RenameSessionRequest
)

from models.chat_models import (
    ChatRequest
)
from database.models import ChatSession

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
        "sources": message.sources,
        "created_at": (
            message.created_at.isoformat()
            if message.created_at
            else None
        )
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

    # Auto-title first message
    if session.title == "New Chat":

        update_session_title(
            session_id=session.id,
            title=request.message[:40],
            db=db
        )

   

    # ==========================
    # Conversation-Aware Retrieval
    # ==========================

    recent_messages = (
    get_recent_messages(
        session_id=request.session_id,
        limit=5,
        db=db
    )
)

    contextual_query = ""

# Skip newest message because it was
# already saved and is request.message

    for msg in reversed(
        recent_messages
):
        if msg.sender == "user":

            contextual_query += (
                msg.content + "\n"
            )

    contextual_query += (
        request.message
    )

    contextual_query += (
    request.message
)

    print(
        "CONTEXTUAL QUERY:"
    )

    print(
        contextual_query
    )

    rewritten_query = rewrite_query(
        contextual_query,
        recent_messages
    )

    print(
        "REWRITTEN QUERY:"
    )

    print(
        rewritten_query
    )

    # ==========================
    # Retrieval
    # ==========================

    retrieved_chunks, metadata = (
        retrieve_relevant_chunks(
            query=rewritten_query,
            user_id=user.id,
            collection_name=request.knowledge_base
        )
    )

     # Save user message
    save_message(
        session_id=request.session_id,
        sender="user",
        content=request.message,
        sources="",
        db=db
    )

    history_messages = (
        get_recent_messages(
            session_id=request.session_id,
            limit=6,
            db=db
        )
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

    if session.title == "New Chat":

        update_session_title(
            session_id=session.id,
            title=request.message[:40],
            db=db
        )

    # =========================
    # SAVE USER MESSAGE
    # =========================

    save_message(
        session_id=request.session_id,
        sender="user",
        content=request.message,
        sources="",
        db=db
    )

# =========================
# AGENT TOOL SELECTION
# =========================

    selected_tool = choose_tool(
    request.message
)
    
    planned_tools = plan_tools(
    request.message
)

    print(
        "PLANNED TOOLS:",
       planned_tools
)

    if len(planned_tools) > 1:

        print(
        "AGENT MODE: MULTI TOOL"
    )

    else:

        print(
        "AGENT TOOL:",
        selected_tool
    )
    
    if len(planned_tools) > 1:

        results = []

        if "compare_documents" in planned_tools:

            print(
            "EXECUTING TOOL: compare_documents"
        )

            results.append(

              compare_documents(
                user_id=user.id,
                collection_name=request.knowledge_base
            )

        )

        if "summarize_document" in planned_tools:

           print(
            "EXECUTING TOOL: summarize_document"
        )

           results.append(

            summarize_documents(
                user_id=user.id,
                collection_name=request.knowledge_base
            )

        )

        if "generate_report" in planned_tools:

           print(
            "EXECUTING TOOL: generate_report"
        )

           results.append(

            generate_document_report(
                user_id=user.id,
                collection_name=request.knowledge_base
            )

        )

        print(
          "TOOLS EXECUTED:",
           len(results)
    )

        final_response = synthesize_tool_results(
           request.message,
           results
    )

        save_message(
          session_id=request.session_id,
          sender="bot",
          content=final_response,
          sources="",
          db=db
    )

        return StreamingResponse(
           iter([final_response]),
           media_type="text/plain"
    )

    if selected_tool == "job_match":

        result = match_job_requirements(
            user_id=user.id,
            collection_name=request.knowledge_base
    )

        save_message(
        session_id=request.session_id,
        sender="bot",
        content=result,
        sources="",
        db=db
    )

        return StreamingResponse(
        iter([result]),
        media_type="text/plain"
    )
    
   

# =========================
# TOOL: SUMMARIZE DOCUMENTS
# =========================

    if selected_tool == "summarize_document":

        summary = summarize_documents(
        user_id=user.id,
        collection_name=request.knowledge_base
    )

        save_message(
        session_id=request.session_id,
        sender="user",
        content=request.message,
        sources="",
        db=db
    )

        save_message(
        session_id=request.session_id,
        sender="bot",
        content=summary,
        sources="",
        db=db
    )

        def generate():

          yield summary

        return StreamingResponse(
        generate(),
        media_type="text/plain"
    )


# =========================
# TOOL: GENERATE REPORT
# =========================

    if selected_tool == "generate_report":

        report = generate_document_report(
        user_id=user.id,
        collection_name=request.knowledge_base
    )

        save_message(
        session_id=request.session_id,
        sender="user",
        content=request.message,
        sources="",
        db=db
    )

        save_message(
        session_id=request.session_id,
        sender="bot",
        content=report,
        sources="",
        db=db
    )

        def generate():

          yield report

        return StreamingResponse(
        generate(),
        media_type="text/plain"
    )


# =========================
# TOOL: COMPARE DOCUMENTS
# =========================

    if selected_tool == "compare_documents":

        comparison = compare_documents(
        user_id=user.id,
        collection_name=request.knowledge_base
    )

        save_message(
        session_id=request.session_id,
        sender="user",
        content=request.message,
        sources="",
        db=db
    )

        save_message(
        session_id=request.session_id,
        sender="bot",
        content=comparison,
        sources="",
        db=db
    )

        return StreamingResponse(
          iter([comparison]),
           media_type="text/plain"
    )

    

    # =========================
    # TOOL: LIST DOCUMENTS
    # =========================

    if selected_tool == "list_documents":

        documents = get_documents(
            user_id=user.id,
            collection_name=request.knowledge_base
    )

        if not documents:

            response_text = (
            "No documents uploaded."
        )

        else:

            response_text = (
            "Uploaded Documents:\n\n"
            + "\n".join(
                f"• {doc}"
                for doc in documents
            )
        )

        save_message(
           session_id=request.session_id,
           sender="bot",
           content=response_text,
           sources="",
           db=db
    )

        return StreamingResponse(
           iter([response_text]),
           media_type="text/plain"
    )

    # =========================
    # TOOL: ANALYTICS
    # =========================

    if selected_tool == "analytics":

        user_sessions = (
           db.query(ChatSession)
           .filter(
              ChatSession.user_id == user.id
        )
            .all()
    )

        session_ids = [
           session.id
           for session in user_sessions
    ]

        metrics = (
           db.query(EvaluationMetric)
           .filter(
                EvaluationMetric.session_id.in_(
                   session_ids
            )
        )
            .all()
    )

        total = len(metrics)

        if total == 0:

            response_text = (
               "No evaluation metrics available."
        )

        else:

            avg_relevancy = sum(
            float(m.answer_relevancy)
            for m in metrics
        ) / total

            avg_faithfulness = sum(
            float(m.faithfulness)
            for m in metrics
        ) / total

            avg_precision = sum(
            float(m.context_precision)
            for m in metrics
        ) / total

            response_text = f"""
    RAG Analytics

    Relevancy:
    {avg_relevancy:.2%}

    Faithfulness:
    {avg_faithfulness:.2%}

    Context Precision:
    {avg_precision:.2%}
 
    Evaluations:
    {total}
    """

        save_message(
           session_id=request.session_id,
           sender="bot",
           content=response_text,
           sources="",
           db=db
    )

        return StreamingResponse(
           iter([response_text]),
           media_type="text/plain"
    )

    # =========================
    # CONVERSATION RETRIEVAL
    # =========================

    recent_messages = (
        get_recent_messages(
            session_id=request.session_id,
            limit=5,
            db=db
        )
    )

    contextual_query = ""

    for msg in reversed(
        recent_messages
    ):

        if msg.sender == "user":

            contextual_query += (
                msg.content + "\n"
            )

    contextual_query += (
        request.message
    )

    print(
        "CONTEXTUAL QUERY:"
    )

    print(
        contextual_query
    )

    rewritten_query = rewrite_query(
        contextual_query,
        recent_messages
    )

    search_queries = (
        generate_search_queries(
            rewritten_query
        )
    )

    if not search_queries:

        search_queries = [
            rewritten_query
        ]

    print(
        "SEARCH QUERIES:"
    )

    print(
        search_queries
    )

    retrieved_chunks, metadata = (
        retrieve_multi_query_chunks(
            queries=search_queries,
            user_id=user.id,
            collection_name=request.knowledge_base
        )
    )

    history_messages = (
        get_recent_messages(
            session_id=request.session_id,
            limit=6,
            db=db
        )
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

        answer_relevancy = (
            calculate_answer_relevancy(
                request.message,
                full_response
            )
        )

        faithfulness = (
            calculate_faithfulness(
                full_response,
                retrieved_chunks
            )
        )

        context_precision = (
            calculate_context_precision(
                request.message,
                retrieved_chunks
            )
        )

        save_evaluation_metric(

            session_id=request.session_id,

            answer_relevancy=
                answer_relevancy,

            faithfulness=
                faithfulness,

            context_precision=
                context_precision,

            db=db
        )

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

@router.get("/analytics")
def analytics(
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

    sessions = (
        db.query(ChatSession)
        .filter(
            ChatSession.user_id
            == user.id
        )
        .all()
    )

    session_ids = [
        session.id
        for session in sessions
    ]

    metrics = (
        db.query(EvaluationMetric)
        .filter(
            EvaluationMetric.session_id.in_(
                session_ids
            )
        )
        .all()
    )

    if not metrics:

        return {
            "avg_relevancy": 0,
            "avg_faithfulness": 0,
            "avg_precision": 0,
            "total_evaluations": 0
        }

    avg_relevancy = sum(
        float(m.answer_relevancy)
        for m in metrics
    ) / len(metrics)

    avg_faithfulness = sum(
        float(m.faithfulness)
        for m in metrics
    ) / len(metrics)

    avg_precision = sum(
        float(m.context_precision)
        for m in metrics
    ) / len(metrics)

    return {

        "avg_relevancy":
            round(
                avg_relevancy,
                3
            ),

        "avg_faithfulness":
            round(
                avg_faithfulness,
                3
            ),

        "avg_precision":
            round(
                avg_precision,
                3
            ),

        "total_evaluations":
            len(metrics)
    }

