from app.llm.client import llm
from app.router.query_router import route_query
from app.chains.rag_chain import rag_chain


def answer_query(query: str) -> str:

    route = route_query(query)

    if route == "rag":
        return rag_chain(query)

    return llm.invoke(query).content