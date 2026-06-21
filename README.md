# PDF Q&A — Agentic RAG (Streamlit + Groq)

Upload a PDF, ask questions, get answers grounded only in that document —
with page citations. Built on an agentic RAG pipeline: router → query
rewrite → decomposition → multi-query expansion → hybrid BM25 + vector
retrieval → reranking → evidence check → answer generation → grounding
verification.

Runs on Groq's free hosted LLM API, so it can be deployed for free with no
local GPU or model server needed.

## How it works

1. You upload a PDF and click **Ask** to build the index (chunking, BM25
   keyword index, vector embeddings, reranker — all in memory, per
   session).
2. Each question goes through:
   - **Router** — decides if you're asking for a summary, asking about
     chat history, asking something unrelated to the document, or asking
     a real question about it.
   - **Rewrite + decomposition** — turns your question into one or more
     standalone search queries.
   - **Hybrid retrieval** — pulls candidate chunks via both keyword (BM25)
     and semantic (vector) search.
   - **Reranking** — scores chunks against each sub-question, with a fair
     allocation so a multi-part question doesn't let one part starve out
     another.
   - **Evidence check** — if the first pass doesn't have enough context,
     it does a broader fallback retrieval before answering.
   - **Answer generation** — answers only from the retrieved document
     context, citing source pages.
   - **Grounding check** — independently verifies the generated answer
     didn't add anything not actually in the document (catches the model
     padding a refusal with invented suggestions).

## Files

```
.
├── app.py             # Streamlit UI — upload, build index, chat
├── llm.py             # Groq chat wrapper (per-user API key, no server-side caching of keys)
├── loader.py           # PDF loading from an uploaded file
├── summarizer.py        # document summary (used by the SUMMARY route)
├── chunker.py          # RecursiveCharacterTextSplitter
├── bm25_search.py        # BM25 keyword index
├── vector_store.py        # HuggingFace embeddings + Chroma vector store
├── reranker.py          # CrossEncoder reranker
├── qa_pipeline.py        # the full agentic pipeline, one call per question
├── requirements.txt
├── .gitignore
└── .streamlit/
    └── secrets.toml.example
```

## Bring your own Groq key

This app does **not** ship with a built-in API key. Every user — including
you — pastes their own free Groq key into the sidebar each time they use
it. Nothing is stored server-side; the key lives only in that browser's
session. This keeps usage and free-tier rate limits separate per person,
and means no one's API spend is shared with anyone else.

Get a free key at **[console.groq.com](https://console.groq.com)** → sign
up (no credit card) → API Keys → Create key. Free tier: 30 requests/min,
6,000 tokens/min — fine for casual use by one person at a time.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

It opens in your browser. Paste your Groq key into the sidebar, upload a
PDF, click **Ask** to build the index, then ask questions in the chat box.

(`.streamlit/secrets.toml.example` exists only as a template if you ever
want a local default key for your own testing — copy it to
`secrets.toml` and fill it in. It's git-ignored, so it never gets
committed or pushed.)

