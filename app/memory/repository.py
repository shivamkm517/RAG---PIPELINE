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
    meta_data: dict | None = None,
) -> Message:
    message = Message(
        thread_id=thread_id,
        role=role,
        content=content,
        meta_data=meta_data,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def get_thread_messages(
    db: Session,
    thread_id: int,
    limit: int | None = None,
) -> list[Message]:
    statement = (
        select(Message)
        .where(Message.thread_id == thread_id)
        .order_by(Message.id.asc())
    )
    if limit:
        statement = statement.limit(limit)

    return list(db.scalars(statement).all())



def get_all_threads(db: Session) -> list[Thread]:
    statement = select(Thread).order_by(Thread.updated_at.desc())
    return list(db.scalars(statement).all())


def get_thread_by_id(db: Session, thread_id: int) -> Thread | None:
    statement = select(Thread).where(Thread.id == thread_id)
    return db.scalars(statement).first()


def delete_thread(db: Session, thread_id: int) -> bool:
    thread = get_thread_by_id(db, thread_id)
    if thread:
        db.delete(thread)
        db.commit()
        return True
    return False