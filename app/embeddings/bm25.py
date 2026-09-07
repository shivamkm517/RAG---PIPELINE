import re

from rank_bm25 import BM25Okapi


def tokenize(text: str) -> list[str]:
    """
    Convert text into tokens for BM25.
    """

    return re.findall(
        r"\b\w+\b",    # finding all the words in the text
        text.lower(),  # converting into the lower case to make the search case-insensitive
    )


class BM25Index:

    def __init__(self, chunks: list[dict]):

        if not chunks:
            raise ValueError("Cannot create BM25 index from empty chunks.")

        self.chunks = chunks  # initalize the chunks attribute with the provided chunks

        tokenized_corpus = [
            tokenize(chunk["text"]) # tokenize the text of each chunk, Using the tokenize function defined earlier
            for chunk in chunks
        ]

        self.bm25 = BM25Okapi(tokenized_corpus) # create a BM25 index using the tokenized corpus

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:
        """
        Search the BM25 index for the given query and return the top_k results.
        """

        query_tokens = tokenize(query)

        scores = self.bm25.get_scores(query_tokens) # compute the BM25 scores for the query tokens against the indexed chunks

        ranked_indices = scores.argsort()[::-1][:top_k] # get the indices of the top_k highest scores in descending order

        results = [] # initialize an empty list to store the search results

        for rank, index in enumerate(ranked_indices):

            results.append(
                {
                    "chunk": self.chunks[index],
                    "score": float(scores[index]),
                    "rank": rank + 1,
                }
            )

        return results