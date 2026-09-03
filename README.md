                         ┌─────────────────────────┐
                         │       USER / CLIENT     │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │       FASTAPI API       │
                         └────────────┬────────────┘
                                      │
                                      ▼
              ╔════════════════════════════════════════╗
              ║           LAYER 8                      ║
              ║  Guardrails + Observability            ║
              ║  - Prompt injection detection          ║
              ║  - Citation validation                 ║
              ║  - Tracing                             ║
              ╚════════════════════╤═══════════════════╝
                                   │
                                   ▼
              ╔════════════════════════════════════════╗
              ║           LAYER 4                      ║
              ║          LANGGRAPH                     ║
              ║                                        ║
              ║   Query Router                         ║
              ║      │                                 ║
              ║      ├── Paper Q&A                     ║
              ║      ├── Paper Comparison              ║
              ║      └── Summarization                 ║
              ╚════════════════════╤═══════════════════╝
                                   │
                    ┌──────────────┼───────────────┐
                    │              │               │
                    ▼              ▼               ▼
              ╔══════════╗   ╔══════════╗   ╔══════════╗
              ║ LAYER 6  ║   ║ LAYER 3  ║   ║ LAYER 5  ║
              ║ MEMORY   ║   ║ QDRANT   ║   ║ LLM      ║
              ║          ║   ║          ║   ║          ║
              ║ Redis    ║   ║ Vectors  ║   ║ Claude   ║
              ║ Postgres ║   ║ + BM25   ║   ║          ║
              ╚══════════╝   ╚────┬─────╝   ╚────┬─────╝
                                   │              │
                                   │              │
                              ╔════▼═════╗        │
                              ║ LAYER 2  ║        │
                              ║Embedding ║        │
                              ║          ║        │
                              ║ Cohere   ║        │
                              ╚════▲═════╝        │
                                   │              │
                              ╔════╧═════╗        │
                              ║ LAYER 1  ║        │
                              ║ Parsing  ║        │
                              ║          ║        │
                              ║ Docling  ║        │
                              ╚════▲═════╝        │
                                   │              │
                                   │              │
                              ┌────┴─────┐        │
                              │   PDF    │        │
                              └──────────┘        │
                                                  │
              ╔═══════════════════════════════════╧════╗
              ║              LAYER 7                   ║
              ║              EVALUATION                ║
              ║                                        ║
              ║ Ragas → Faithfulness                   ║
              ║        Context Precision               ║
              ║        Context Recall                  ║
              ║        Answer Relevancy                ║
              ╚════════════════════════════════════════╝