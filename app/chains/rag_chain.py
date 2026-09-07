from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate

from app.llm.client import llm
from app.retrieval.hybrid_retriever import HybridRetriever


retriever = HybridRetriever()

prompt = ChatPromptTemplate.from_template(
    """
You are a document question-answering assistant.

Use the conversation history and provided context to understand
the user's current question.

Answer using ONLY information supported by the context.

Conversation history:
{history}

Context:
{context}

Current question:
{question}

Answer:
"""
)


def rag_chain(
    query: str,
    history: list[dict] | None = None,
) -> str:

    results = retriever.search(
        query=query,
        top_k=5,
    )

    context = "\n\n".join(
        result["chunk"]["text"]
        for result in results
    )

    history_text = ""

    if history:
        history_text = "\n".join(
            f"{message['role']}: {message['content']}"
            for message in history
        )

    messages = prompt.format_messages(
        history=history_text,
        context=context,
        question=query,
    )

    response = llm.invoke(messages)

    return response.content