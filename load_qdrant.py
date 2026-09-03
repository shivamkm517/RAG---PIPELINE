import json

from app.vectorstore.qdrant_store import (
    QdrantVectorStore,
)


INPUT_FILE = (
    "data/processed/embedded_chunks.json"
)


def main():

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        chunks = json.load(file)

    print(
        f"Loaded {len(chunks)} chunks."
    )

    store = QdrantVectorStore()

    store.create_collection()

    store.insert_chunks(
        chunks
    )


if __name__ == "__main__":
    main()