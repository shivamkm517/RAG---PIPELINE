import os

import cohere
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("COHERE_API_KEY")

if not API_KEY:
    raise ValueError(
        "Cohere API key not found. "
        "Please set the COHERE_API_KEY environment variable."
    )


client = cohere.ClientV2(api_key=API_KEY)

MODEL = "embed-v4.0"
DIMENSION = 1024


def generate_embeddings(
    texts: list[str],
    input_type: str = "search_document",
) -> list[list[float]]:
    """
    Generate embeddings using Cohere.

    input_type:
        search_document -> used for document chunks
        search_query    -> used for user queries
    """

    response = client.embed(
        model=MODEL,
        texts=texts,
        input_type=input_type,
        output_dimension=DIMENSION,
        embedding_types=["float"],
    )

    return response.embeddings.float


def generate_query_embedding(
    query: str,
) -> list[float]:
    """
    Generate an embedding for a user query.
    """

    embeddings = generate_embeddings(
        texts=[query],
        input_type="search_query",
    )

    return embeddings[0]