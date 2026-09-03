import json

from app.embeddings.bm25 import BM25Index


with open(
    "data/processed/chunks.json",
    "r",
    encoding="utf-8",
) as file:

    chunks = json.load(file)


index = BM25Index(chunks)


query = "authentication"


results = index.search(
    query=query,
    top_k=5,
)


print("\nBM25 RESULTS")
print("=" * 70)


for result in results:

    chunk = result["chunk"]

    print(f"\nRank: {result['rank']}")
    print(f"Score: {result['score']:.4f}")

    print(
        "Section:",
        chunk["metadata"].get("section"),
    )

    print(
        "Text:",
        chunk["text"][:300],
    )