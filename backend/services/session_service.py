from datetime import datetime

from sqlalchemy.orm import Session

from backend.database.models import (
    ChatSession,
    ChatMessage
)


def create_session(
    user_id,
    title="New Chat",
    knowledge_base="general",
    db: Session = None
):

    session = ChatSession(
        user_id=user_id,
        title=title,
        knowledge_base=knowledge_base
    )

    db.add(session)

    db.commit()

    db.refresh(session)

    return session


def get_user_sessions(
    user_id,
    db: Session
):

    return (
        db.query(ChatSession)
        .filter(
            ChatSession.user_id == user_id
        )
        .order_by(
            ChatSession.updated_at.desc()
        )
        .all()
    )


def delete_session(
    session_id,
    user_id,
    db: Session
):

    session = (
        db.query(ChatSession)
        .filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        )
        .first()
    )

    if not session:

        return False

    db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).delete()

    db.delete(session)

    db.commit()

    return True


def save_message(
    session_id,
    sender,
    content,
    sources,
    db: Session
):

    message = ChatMessage(
        session_id=session_id,
        sender=sender,
        content=content,
        sources=sources
    )

    db.add(message)

    session = (
        db.query(ChatSession)
        .filter(
            ChatSession.id == session_id
        )
        .first()
    )

    if session:

        session.updated_at = datetime.utcnow()

    db.commit()

    db.refresh(message)

    return message


def get_session_messages(
    session_id,
    user_id,
    db: Session
):

    session = (
        db.query(ChatSession)
        .filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        )
        .first()
    )

    if not session:

        return []

    return (
        db.query(ChatMessage)
        .filter(
            ChatMessage.session_id == session_id
        )
        .order_by(
            ChatMessage.created_at.asc()
        )
        .all()
    )


def update_session_title(
    session_id: int,
    title: str,
    db
):

    session = (
        db.query(ChatSession)
        .filter(
            ChatSession.id == session_id
        )
        .first()
    )

    if not session:

        return None

    session.title = title

    session.updated_at = datetime.utcnow()

    db.commit()

    return session