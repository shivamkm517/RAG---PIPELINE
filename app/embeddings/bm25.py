import re

from rank_bm25 import BM25Okapi


def tokenize(text: str) -> list[str]:
    """
    Convert text into tokens for BM25.
    """

    return re.findall(
        r"\b\w+\b",
        text.lower(),
    )


class BM25Index:

    def __init__(self, chunks: list[dict]):

        if not chunks:
            raise ValueError("Cannot create BM25 index from empty chunks.")

        self.chunks = chunks

        tokenized_corpus = [
            tokenize(chunk["text"])
            for chunk in chunks
        ]

        self.bm25 = BM25Okapi(tokenized_corpus)

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:

        query_tokens = tokenize(query)

        scores = self.bm25.get_scores(query_tokens)

        ranked_indices = scores.argsort()[::-1][:top_k]

        results = []

        for rank, index in enumerate(ranked_indices):

            results.append(
                {
                    "chunk": self.chunks[index],
                    "score": float(scores[index]),
                    "rank": rank + 1,
                }
            )

        return results