from app.embeddings.hybrid_search import (
    HybridRetriever,
)


retriever = HybridRetriever()


query = "How does the system authenticate users?"


results = retriever.semantic_search(
    query=query,
    top_k=5,
)


print("\nSEMANTIC SEARCH")
print("=" * 70)


for rank, result in enumerate(
    results,
    start=1,
):

    chunk = result["chunk"]

    print(f"\nRank: {rank}")

    print(
        f"Score: {result['score']:.4f}"
    )

    print(
        "Section:",
        chunk["metadata"].get("section"),
    )

    print(
        "Text:",
        chunk["text"][:300],
    )