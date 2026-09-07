from app.router.query_router import route_query


queries = [
    "What is the main purpose of WorkHub?",
    "What is the capital of France?",
]

for query in queries:
    route = route_query(query)

    print(f"\nQuery: {query}")
    print(f"Route: {route}")