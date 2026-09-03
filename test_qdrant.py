from app.embeddings.cohere_embeddings import (
    generate_query_embedding,
)

from app.vectorstore.qdrant_store import (
    QdrantVectorStore,
)


query = "How does authentication work?"


query_vector = generate_query_embedding(
    query
)


store = QdrantVectorStore()


results = store.search(
    query_vector=query_vector,
    top_k=5,
)


print("\nQDRANT RESULTS")
print("=" * 70)


for rank, result in enumerate(
    results,
    start=1,
):

    print(f"\nRank: {rank}")

    print(
        f"Score: {result.score:.4f}"
    )

    print(
        "Chunk ID:",
        result.payload["chunk_id"],
    )

    print(
        "Text:",
        result.payload["text"][:500],
    )

    print(
        "Metadata:",
        result.payload["metadata"],
    )