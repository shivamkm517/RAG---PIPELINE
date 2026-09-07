from langchain_core.messages import HumanMessage, AIMessage

from app.llm.client import llm
from app.router.query_router import route_query
from app.chains.rag_chain import rag_chain

from app.memory.database import SessionLocal
from app.memory.repository import add_message, get_thread_messages


def answer_query(query: str, thread_id: int) -> str:
    db = SessionLocal()

    try:
        previous_messages = get_thread_messages(db, thread_id)

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

        return answer

    finally:
        db.close()