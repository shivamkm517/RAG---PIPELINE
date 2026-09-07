from langchain_core.prompts import ChatPromptTemplate

from app.llm.client import llm
from app.retrieval.hybrid_retriever import HybridRetriever

retriever = HybridRetriever()


prompt = ChatPromptTemplate.from_template(
    """
You are a document question-answering assistant.

Answer the question based on the context below.

The context may express the answer using different wording.
You should understand the meaning of the context and answer
the question accordingly.

Do NOT require the exact words from the question to appear
in the context.

Only use information supported by the context.
Do not add outside information.

If the context genuinely does not contain enough information,
say:
"I don't have enough information in the provided documents."

Context:
{context}

Question:
{question}

Answer:
"""
)


def rag_chain(query: str) -> str:

    results = retriever.search(
        query=query,
        top_k=5,
    )

    context = "\n\n".join(
        result["chunk"]["text"]
        for result in results
    )

    messages = prompt.format_messages(
        context=context,
        question=query,
    )

    response = llm.invoke(messages)

    return response.content