from langchain_core.messages import HumanMessage, AIMessage

from app.llm.client import llm
from app.router.query_router import route_query
from app.chains.rag_chain import rag_chain

from app.memory.database import SessionLocal
from datetime import datetime
from app.memory.repository import add_message, get_thread_messages, get_thread_by_id


def answer_query(query: str, thread_id: int) -> dict:
    db = SessionLocal()

    try:
        previous_messages = get_thread_messages(db, thread_id)

        # Update thread title if empty or default
        thread = get_thread_by_id(db, thread_id)
        if thread:
            thread.updated_at = datetime.utcnow()
            if not thread.title or thread.title == "New Chat":
                thread.title = query[:40] + ("..." if len(query) > 40 else "")
            db.commit()

        history = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in previous_messages
        ]

        add_message(
            db,
            thread_id,
            "user",
            query,
        )

        route = route_query(query)

        if route == "rag":
            answer = rag_chain(
                query=query,
                history=history,
            )
        else:
            messages = []

            for message in previous_messages:
                if message.role == "user":
                    messages.append(
                        HumanMessage(content=message.content)
                    )
                else:
                    messages.append(
                        AIMessage(content=message.content)
                    )

            messages.append(HumanMessage(content=query))

            response = llm.invoke(messages)
            answer = response.content

        add_message(
            db,
            thread_id,
            "assistant",
            answer,
        )

        return {
            "answer": answer,
            "route": route,
            "thread_id": thread_id,
        }

    finally:
        db.close()