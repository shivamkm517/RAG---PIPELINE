from app.vectorstore.qdrant_store import (
    QdrantVectorStore,
)


store = QdrantVectorStore()

store.create_collection()