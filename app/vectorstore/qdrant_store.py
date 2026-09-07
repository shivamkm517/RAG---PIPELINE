from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)


QDRANT_PATH = "data/qdrant"   # Fetching the Qdrant data path

COLLECTION_NAME = "paperpilot_chunks"

VECTOR_SIZE = 1024 # Size of the vector embeddings


class QdrantVectorStore:

    def __init__(self):

        self.client = QdrantClient(
            path=QDRANT_PATH
        )

    def create_collection(self):

        collections = self.client.get_collections() 

        existing_collections = [
            collection.name
            for collection in collections.collections
        ]

        if COLLECTION_NAME not in existing_collections:

            self.client.create_collection(
                collection_name=COLLECTION_NAME,

                vectors_config=VectorParams(
                    size=VECTOR_SIZE,
                    distance=Distance.COSINE,
                ),
            )

            print(
                f"Created collection: {COLLECTION_NAME}"
            )

        else:

            print(
                f"Collection already exists: "
                f"{COLLECTION_NAME}"
            )

    def insert_chunks(
        self,
        chunks: list[dict],
    ):

        points = []

        for index, chunk in enumerate(chunks):

            embedding = chunk["embedding"]

            payload = {
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "metadata": chunk["metadata"],
            }

            point = PointStruct(
                id=index,
                vector=embedding,
                payload=payload,
            )

            points.append(point)

        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
        )

        print(
            f"Inserted {len(points)} chunks "
            f"into Qdrant."
        )

    def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
    ):

        results = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=top_k,
        ).points

        return results

    def close(self):
        self.client.close()