# PaperPilot RAG Chatbot - Complete System Architecture & Execution Flow

This document provides a comprehensive, end-to-end technical explanation of how the **PaperPilot RAG Chatbot** works. It covers the system architecture, component breakdown, data ingestion pipeline, query routing strategy, hybrid retrieval fusion, memory management, FastAPI backend APIs, and web front-end execution flow.

---

## 1. System Architecture Overview

PaperPilot is a **Hybrid Retrieval-Augmented Generation (RAG)** system integrated with an **Intelligent Query Router**, **SQL-based Conversation Memory**, **FastAPI REST Services**, and a modern **Web Single Page Application (SPA)**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER / WEB FRONT-END                              │
│         (HTML5 / CSS3 Glassmorphism / JavaScript / Marked.js / HLJS)       │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTP REST Requests
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                             FASTAPI BACKEND                                 │
│      Endpoints: /api/chat | /api/threads | /api/upload | /api/health        │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CONVERSATION MEMORY LAYER                           │
│        SQLAlchemy ORM ──► PostgreSQL / SQLite (threads & messages)          │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         INTELLIGENT QUERY ROUTER                            │
│                 Structured LLM Classifier (RAG vs Direct)                   │
└──────────────────┬───────────────────────────────────────┬──────────────────┘
                   │                                       │
      Route: "rag" │                                       │ Route: "direct"
                   ▼                                       ▼
┌─────────────────────────────────────┐ ┌─────────────────────────────────────┐
│       HYBRID RETRIEVAL ENGINE       │ │           DIRECT LLM PATH           │
│ ┌─────────────────────────────────┐ │ │                                     │
│ │  Semantic Search: Cohere +      │ │ │   Pass conversation history +       │
│ │  Qdrant Vector Store (Cosine)   │ │ │   current user question directly    │
│ └────────────────┬────────────────┘ │ │   to LLM model (Llama 3.2).         │
│                  │                  │ └──────────────────┬──────────────────┘
│ ┌────────────────┴────────────────┐ │                    │
│ │  Keyword Search: BM25 Index     │ │                    │
│ └────────────────┬────────────────┘ │                    │
│                  │                  │                    │
│ ┌────────────────▼────────────────┐ │                    │
│ │ Reciprocal Rank Fusion (RRF)    │ │                    │
│ └────────────────┬────────────────┘ │                    │
│                  │ Top 5 Chunks     │                    │
│                  ▼                  │                    │
│ ┌─────────────────────────────────┐ │                    │
│ │ Context-Augmented Prompt        │ │                    │
│ └────────────────┬────────────────┘ │                    │
└──────────────────┼──────────────────┘                    │
                   │                                       │
                   ▼                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                LLM GENERATION                               │
│                         Ollama / Llama 3.2 / LangChain                      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     RESPONSE & MEMORY PERSISTENCE                           │
│    Store User & Assistant Messages in DB ──► Return JSON to Front-End       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Components & Layer Breakdown

### Layer 1: Ingestion & Document Processing (`app/ingestion/`)
- **Parser (`parser.py`)**: Uses **Docling** to parse raw PDF files uploaded into `data/raw/`. It extracts text content, document layout, tables, and section headings.
- **Cleaner (`cleaner.py`)**: Normalizes whitespace, removes header/footer noise, and prepares clean text payloads.
- **Chunker (`chunker.py`)**: Splits documents into semantically coherent text chunks with overlapping windows and attaches metadata (such as page number and section title).

---

### Layer 2: Vector Store & Keyword Indexing (`app/embeddings/`, `app/vectorstore/`)
- **Dense Embeddings (`cohere_embeddings.py`)**: Converts chunk texts and search queries into dense vector representations (dimension = 1024) using Cohere Embed models.
- **Vector Database (`qdrant_store.py`)**: Local embedded **Qdrant Vector Store** stored in `data/qdrant/`. Manages collection `paperpilot_chunks` configured with Cosine Similarity.
- **Sparse Keyword Index (`bm25.py`)**: Builds a **BM25Okapi** index over the tokenized chunk collection for exact term matching.

---

### Layer 3: Hybrid Retrieval & Reciprocal Rank Fusion (`app/retrieval/hybrid_retriever.py`)
To maximize recall and precision, PaperPilot combines dense semantic search with sparse keyword search using **Reciprocal Rank Fusion (RRF)**:

1. **Semantic Search**: Queries Qdrant for top-$k$ nearest neighbors by vector similarity.
2. **BM25 Search**: Queries BM25 index for top-$k$ exact keyword matches.
3. **RRF Scoring Formula**:
   $$\text{RRF\_Score}(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$
   *where $k = 60$, and $r_m(d)$ is the rank of document $d$ in retrieval method $m$.*
4. The top 5 highest scoring chunks are assembled into the ground-truth context window.

---

### Layer 4: Query Router (`app/router/query_router.py`)
Before running expensive vector retrieval, an LLM classifier analyzes the user's input:
- **`rag` Route**: Triggered when the query pertains to uploaded documents, WorkHub requirements, features, architecture, or specific specs.
- **`direct` Route**: Triggered for general knowledge questions (e.g., "What is Python?", "Calculate 25 * 4") or casual conversational greetings.

---

### Layer 5: Memory & Database Layer (`app/memory/`)
- **Database Connection (`database.py`)**: Uses SQLAlchemy with `DATABASE_URL` configuration. Defaults to SQLite (`sqlite:///./paperpilot.db`) or PostgreSQL if configured.
- **ORM Models (`models.py`)**:
  - `Thread`: Represents a chat thread (`id`, `title`, `created_at`, `updated_at`).
  - `Message`: Stores individual chat turns (`id`, `thread_id`, `role`, `content`, `created_at`).
- **Repository (`repository.py`)**: Helper functions for thread creation (`create_thread`), history retrieval (`get_thread_messages`), thread listing (`get_all_threads`), and deletion (`delete_thread`).

---

### Layer 6: Chains & Execution Logic (`app/chains/`)
- **`rag_chain.py`**: Constructs a strict context-bound prompt:
  ```text
  You are a document question-answering assistant.
  Answer using ONLY information supported by the context.
  
  Conversation history: {history}
  Context: {context}
  Current question: {question}
  ```
- **`query_chain.py`**: Main orchestrator:
  1. Loads message history from SQLite/PostgreSQL for `thread_id`.
  2. Auto-generates thread title if it's the thread's first message.
  3. Classifies query via `route_query(query)`.
  4. Routes query to `rag_chain()` or direct LLM invocation.
  5. Saves both user query and assistant response to database.
  6. Returns response payload containing `{ answer, route, thread_id }`.

---

### Layer 7: FastAPI Server & Web Front-End (`app/main.py`, `static/`)
- **FastAPI Endpoints**:
  - `GET /api/health` -> Health check status.
  - `GET /api/threads` -> Returns list of threads for sidebar navigation.
  - `POST /api/threads` -> Creates new conversation thread.
  - `GET /api/threads/{id}` -> Returns message history for chosen thread.
  - `DELETE /api/threads/{id}` -> Deletes thread and associated messages.
  - `POST /api/chat` -> Processes message, runs chain, returns answer + route.
  - `POST /api/upload` -> Ingests uploaded PDF files.
- **Web UI Features**:
  - Sidebar showing active threads, new chat button, and PDF file dropzone.
  - Chat window displaying route badges (`[RAG: Document Match]` vs `[Direct LLM]`), formatted Markdown (`marked.js`), and code syntax highlighting (`highlight.js`).

---

## 3. End-to-End Execution Flow Diagrams

### Flow A: Document Ingestion Pipeline

```
[ PDF File Upload ]
        │
        ▼
Save PDF to data/raw/
        │
        ▼
Docling Parser (Extract text, tables, headings)
        │
        ▼
Chunker (Create semantic chunks + metadata)
        │
        ├──► Generate Cohere Embeddings ──► Upsert to Qdrant (data/qdrant)
        │
        └──► Tokenize Text ──► Update BM25 Index (data/processed/chunks.json)
```

---

### Flow B: User Chat Request Flow

```
[ User Types Message in Web UI ]
        │
        ▼
POST /api/chat { thread_id, message }
        │
        ▼
Fetch Previous Messages from Database (SessionLocal)
        │
        ▼
Save User Message to DB Table 'messages'
        │
        ▼
Run Query Router (LLM Structured Classifier)
        │
 ┌──────┴────────────────────────────────┐
 │                                       │
 ▼ Route: "rag"                          ▼ Route: "direct"
Hybrid Retrieval (BM25 + Qdrant)        Format History Messages
        │                                        │
Reciprocal Rank Fusion (RRF)                     │
        │                                        │
Build RAG Prompt with Context                    │
        │                                        │
        └──────────────────┬─────────────────────┘
                           │
                           ▼
                 LLM Invoke (Ollama Llama 3.2)
                           │
                           ▼
          Save Assistant Message to DB
                           │
                           ▼
      Return JSON Response: { answer, route, thread_id }
                           │
                           ▼
          Web UI Renders Markdown & Route Badge
```

---

## 4. REST API Endpoint Specification

| Method | Endpoint | Description | Request Payload | Response Payload |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | Check API status | None | `{"status": "ok", "app": "PaperPilot RAG Chat"}` |
| `GET` | `/api/threads` | List all chat threads | None | `[{"id": 1, "title": "WorkHub Intro", "created_at": "..."}]` |
| `POST` | `/api/threads` | Create a new thread | `{"title": "Custom Title"}` | `{"id": 2, "title": "Custom Title"}` |
| `GET` | `/api/threads/{id}` | Get thread history | None | `{"id": 1, "title": "...", "messages": [...]}` |
| `DELETE` | `/api/threads/{id}` | Delete thread | None | `{"success": true, "message": "Thread deleted"}` |
| `POST` | `/api/chat` | Send chat message | `{"thread_id": 1, "message": "What is WorkHub?"}` | `{"thread_id": 1, "title": "...", "answer": "...", "route": "rag"}` |
| `POST` | `/api/upload` | Upload PDF file | `Multipart Form (file)` | `{"filename": "doc.pdf", "status": "uploaded"}` |

---

## 5. How to Run the Complete Stack

1. **Start the FastAPI Server**:
   ```bash
   python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Access Web Interface**:
   Navigate to **`http://localhost:8000`** in your browser.
