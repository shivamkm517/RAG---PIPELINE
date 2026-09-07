from app.chains.query_chain import answer_query


queries = [
    "What is the main purpose of WorkHub?",
    "What is the capital of France?",
]

for query in queries:
    print(f"\nQuery: {query}")
    print("Answer:", answer_query(query))