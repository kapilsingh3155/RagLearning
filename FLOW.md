# RAG App — How It Works

This app is a **Retrieval-Augmented Generation (RAG)** chatbot. It lets you ask questions about your own documents and get answers powered by GPT-4o, with full conversation memory.

---

## Project Structure

```
RagLearning/
├── docs/                          # Your source documents (.txt / .pdf)
├── db/chroma_db/                  # Persisted vector store (auto-created)
├── 1_ingestion_pipeline.py        # One-time: load, chunk, embed, store docs
├── 2_retrieval_pipeline.py        # Dev tool: manually test vector search
├── 4_history_aware_generation.py  # Core RAG logic (rewrite → retrieve → answer)
├── api.py                         # FastAPI app setup
├── main.py                        # Entry point: mounts UI + REST API, starts server
└── .env                           # API keys and server config
```

---

## Phase 1 — One-Time Document Ingestion

> Run once before starting the app: `python 1_ingestion_pipeline.py`

```
docs/*.txt
    │
    ▼
Load all .txt files
(LangChain DirectoryLoader + TextLoader)
    │
    ▼
Split into 1000-character chunks
(CharacterTextSplitter, overlap = 0)
    │
    ▼
Convert each chunk → vector embedding
(OpenAI text-embedding-3-small)
    │
    ▼
Store embeddings in ChromaDB
(persisted to db/chroma_db/, cosine similarity)
```

On subsequent runs, if `db/chroma_db/` already exists, this step is skipped automatically.

---

## Phase 2 — App Startup

> Start the app: `python main.py`

```
main.py
    │
    ├── Loads 4_history_aware_generation module (via importlib)
    ├── Creates FastAPI app
    │
    ├── Mounts Gradio Chat UI ──────────────► GET  /
    │   (gr.ChatInterface → calls ask_question on every user message)
    │
    └── Exposes REST endpoint ──────────────► POST /
        (predict_api → calls ask_question with the JSON prompt)
    │
    ▼
uvicorn serves the app on host/port from .env
```

---

## Phase 3 — Per-Question RAG Flow

> Triggered on every user message (from UI or REST API)

```
User sends a question
    │
    ▼
[If chat history exists]
    │  Rewrite question as a standalone search query
    │  using GPT-4o + prior conversation turns
    │  ("Given history, rewrite this question to be standalone")
    │
    ▼ [else use question as-is]
    │
    ▼
Search ChromaDB for top-3 most relevant document chunks
(cosine similarity on embeddings)
    │
    ▼
Build final prompt:
    SystemMessage  → "You are a helpful assistant..."
  + chat_history   → all prior (question, answer) pairs
  + retrieved docs → the 3 most relevant chunks
  + user question  → the current question
    │
    ▼
Call GPT-4o → generate answer
    │
    ▼
Append (question, answer) to in-memory chat_history
    │
    ▼
Return answer to user
```

---

## Environment Variables (`.env`)

| Variable        | Purpose                        |
|-----------------|--------------------------------|
| `OPENAI_API_KEY`| OpenAI API key for GPT-4o and embeddings |
| `UVICORN_HOST`  | Host to bind the server (e.g. `0.0.0.0`) |
| `UVICORN_PORT`  | Port to run the server (e.g. `7860`) |

---

## Data Flow Summary

```
.txt files  ──[ingest]──►  ChromaDB
                               │
User question ──────────────►  ask_question()
                               │  └─ rewrite with history (GPT-4o)
                               │  └─ retrieve top-3 chunks (ChromaDB)
                               │  └─ generate answer (GPT-4o)
                               │
                           Answer + updated chat_history
```

---

## Key Design Decisions

- **History-aware rewriting**: Before searching the vector store, the question is rewritten using past conversation context so follow-up questions like *"tell me more about that"* resolve correctly.
- **In-memory chat history**: Conversation state is stored as a Python list in `4_history_aware_generation.py`. It resets when the server restarts.
- **Gradio + FastAPI together**: Gradio is mounted as a sub-app inside FastAPI using `gr.mount_gradio_app`, so both the UI and the REST endpoint run on the same port.
- **ChromaDB persistence**: Embeddings are written to disk so you only pay the embedding cost once per document set.
