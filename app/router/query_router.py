from typing import Literal

from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate

from app.llm.client import llm


class RouteQuery(BaseModel):
    route: Literal["rag", "direct"]


router_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a query classifier.

You have access to a document about WorkHub.

Classify the user's question into exactly one route:

rag:
Use this when the question asks about WorkHub,
the uploaded document, its requirements, features,
users, functionality, or any information that could
be contained in the document.

direct:
Use this for general knowledge questions unrelated
to WorkHub or the uploaded document.

Examples:

"What is the main purpose of WorkHub?"
-> rag

"What features does WorkHub provide?"
-> rag

"Who are the users of WorkHub?"
-> rag

"What is the capital of France?"
-> direct

"What is WorkHub?"
-> rag

"Tell me about WorkHub"
-> rag

"Explain WorkHub"
-> rag

"What is Python?"
-> direct
        """,
    ),
    ("human", "{question}"),
])


router = router_prompt | llm.with_structured_output(RouteQuery)


def route_query(question: str) -> str:
    result = router.invoke({"question": question})
    return result.route