# Running the App Locally

## Prerequisites

- Python **3.9** (required — the app is not compatible with 3.10+ due to dependency constraints)
- An **OpenAI API key** — get one at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

---

## Step 1 — Clone / Download the Project

```bash
cd path/to/your/workspace
# place the RagLearning folder here
cd RagLearning
```

---

## Step 2 — Create a Virtual Environment

```bash
python3.9 -m venv venv
source venv/bin/activate      # macOS / Linux
# venv\Scripts\activate       # Windows
```

---

## Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 4 — Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env    # if an example file exists
# or create it manually:
```

```
OPENAI_API_KEY=sk-...your-key-here...
UVICORN_HOST=127.0.0.1
UVICORN_PORT=7860
```

> ⚠️ Never commit your `.env` file to git. It is already listed in `.gitignore`.

---

## Step 5 — Add Your Documents

Place `.txt` files you want the app to answer questions about inside the `docs/` folder:

```
docs/
├── your-document-1.txt
├── your-document-2.txt
└── ...
```

---

## Step 6 — Run the Ingestion Pipeline (One-Time)

This reads your documents, creates embeddings, and saves them to a local ChromaDB database.

```bash
python 1_ingestion_pipeline.py
```

You should see output like:
```
=== RAG Document Ingestion Pipeline ===
Loading documents from docs/...
Splitting documents into chunks...
Creating embeddings and storing in ChromaDB...
✅ Ingestion complete! Your documents are now ready for RAG queries.
```

> You only need to run this once. If `db/chroma_db/` already exists, it will be skipped automatically on subsequent runs.

---

## Step 7 — Start the App

```bash
python main.py
```

The server starts on the host and port from your `.env`. With the default config, open your browser at:

```
http://127.0.0.1:7860
```

You will see the **Gradio chat UI** where you can start asking questions about your documents.

---

## Optional — Test the REST API

The app also exposes a REST endpoint at `POST /`:

```bash
curl -X POST http://127.0.0.1:7860/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is the attention mechanism?"}'
```

---

## Optional — Test Vector Search Only

To manually test what documents get retrieved for a query without running the full app:

```bash
python 2_retrieval_pipeline.py
```

---

## Project Structure (Quick Reference)

```
RagLearning/
├── docs/                          # Your .txt source documents (add files here)
├── db/chroma_db/                  # Auto-created vector store (do not edit)
├── 1_ingestion_pipeline.py        # Run once to index your documents
├── 2_retrieval_pipeline.py        # Optional: test retrieval manually
├── 4_history_aware_generation.py  # Core RAG + conversation logic
├── api.py                         # FastAPI app definition
├── main.py                        # App entry point
├── requirements.txt               # Python dependencies
├── .env                           # Your local secrets (not committed)
├── FLOW.md                        # How the app works (architecture)
└── SETUP.md                       # This file
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ImportError: cannot import name 'HfFolder'` | Run `pip install "huggingface-hub==0.24.7"` |
| `TypeError: unsupported operand type(s) for \|` | You are on Python 3.10+. Switch to Python 3.9 |
| `ModuleNotFoundError: No module named 'xyz'` | Run `pip install -r requirements.txt` with venv activated |
| `No .txt files found in docs/` | Add `.txt` files to the `docs/` folder before ingesting |
| App starts but gives wrong answers | Re-run `1_ingestion_pipeline.py` after updating your docs |
