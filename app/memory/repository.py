from sqlalchemy import select
from sqlalchemy.orm import Session

from app.memory.models import Message, Thread


def create_thread(db: Session, title: str | None = None) -> Thread:
    thread = Thread(title=title)

    db.add(thread)
    db.commit()
    db.refresh(thread)

    return thread


def add_message(
    db: Session,
    thread_id: int,
    role: str,
    content: str,
) -> Message:
    message = Message(
        thread_id=thread_id,
        role=role,
        content=content,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def get_thread_messages(
    db: Session,
    thread_id: int,
) -> list[Message]:
    statement = (
        select(Message)
        .where(Message.thread_id == thread_id)
        .order_by(Message.created_at.asc())
    )

    return list(db.scalars(statement).all())