import json
from pathlib import Path

from app.embeddings.bm25 import BM25Index
from app.embeddings.cohere_embeddings import (
    generate_query_embedding,
)
from app.vectorstore.qdrant_store import (
    QdrantVectorStore,
)


CHUNKS_FILE = Path(
    "data/processed/chunks.json"
)


def reciprocal_rank_fusion(
    semantic_results: list[dict],
    keyword_results: list[dict],
    k: int = 60,
    top_k: int = 5,
):
    """
    Combine semantic and BM25 rankings
    using Reciprocal Rank Fusion.
    """

    scores = {}
    chunks = {}

    # -------------------------
    # Semantic results
    # -------------------------

    for rank, result in enumerate(
        semantic_results,
        start=1,
    ):

        chunk = result["chunk"]

        chunk_id = chunk["chunk_id"]

        scores[chunk_id] = (
            scores.get(chunk_id, 0.0)
            + 1 / (k + rank)
        )

        chunks[chunk_id] = chunk

    # -------------------------
    # BM25 results
    # -------------------------

    for rank, result in enumerate(
        keyword_results,
        start=1,
    ):

        chunk = result["chunk"]

        chunk_id = chunk["chunk_id"]

        scores[chunk_id] = (
            scores.get(chunk_id, 0.0)
            + 1 / (k + rank)
        )

        chunks[chunk_id] = chunk

    # -------------------------
    # Sort by RRF score
    # -------------------------

    ranked = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    results = []

    for chunk_id, score in ranked[:top_k]:

        results.append(
            {
                "chunk": chunks[chunk_id],
                "score": score,
            }
        )

    return results


class HybridRetriever:

    def __init__(self):

        # Load chunks for BM25
        self.chunks = json.loads(
            CHUNKS_FILE.read_text(
                encoding="utf-8"
            )
        )

        # BM25 index
        self.bm25 = BM25Index(
            self.chunks
        )

        # Qdrant vector store
        self.vector_store = QdrantVectorStore()

    # ==================================================
    # Semantic Search
    # ==================================================

    def semantic_search(
        self,
        query: str,
        top_k: int = 5,
    ):

        # Convert query into embedding
        query_embedding = generate_query_embedding(
            query
        )

        # Search Qdrant
        results = self.vector_store.search(
            query_vector=query_embedding,
            top_k=top_k,
        )

        semantic_results = []

        for result in results:

            payload = result.payload

            semantic_results.append(
                {
                    "chunk": payload,
                    "score": result.score,
                }
            )

        return semantic_results

    # ==================================================
    # Keyword Search
    # ==================================================

    def keyword_search(
        self,
        query: str,
        top_k: int = 5,
    ):

        return self.bm25.search(
            query=query,
            top_k=top_k,
        )

    # ==================================================
    # Hybrid Search
    # ==================================================

    def search(
        self,
        query: str,
        top_k: int = 5,
    ):

        # -------------------------
        # Semantic retrieval
        # -------------------------

        semantic_results = self.semantic_search(
            query=query,
            top_k=top_k,
        )

        # -------------------------
        # BM25 retrieval
        # -------------------------

        keyword_results = self.keyword_search(
            query=query,
            top_k=top_k,
        )

        # -------------------------
        # RRF fusion
        # -------------------------

        hybrid_results = reciprocal_rank_fusion(
            semantic_results=semantic_results,
            keyword_results=keyword_results,
            top_k=top_k,
        )

        return hybrid_results