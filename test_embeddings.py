from app.embeddings.cohere_embeddings import generate_embeddings


texts = [
    "FastAPI is used to build the backend API.",
    "PostgreSQL stores persistent user information.",
    "JWT tokens are used for authentication.",
]


embeddings = generate_embeddings(texts)


print("Number of embeddings:", len(embeddings))
print("Embedding dimension:", len(embeddings[0]))
print("First 5 values:", embeddings[0][:5])