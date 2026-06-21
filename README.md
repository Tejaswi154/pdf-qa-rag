# PDF Q&A — Agentic RAG (Streamlit + Groq)

Interactive web app version of the Repo Whisperer RAG pipeline. Upload a
PDF, ask questions, get cited answers — powered by the same agentic
pipeline (router → rewrite → decompose → multi-query → hybrid BM25+vector
retrieval → rerank → evidence check → answer → self-verify/correct), just
swapped from local Ollama to Groq's free hosted API so it can run on free
hosting.

## What changed vs. the local notebook/CLI version

- **LLM**: `ollama.chat()` → Groq's hosted API (`llama-3.1-8b-instant`),
  via `llm.py`. Free tier, no local GPU/daemon needed.
- **PDF source**: hardcoded file path → user upload in the browser.
- **Interface**: `input()` loop in a terminal → Streamlit chat UI.
- **Models**: embeddings (`bge-small-en-v1.5`) and reranker
  (`ms-marco-MiniLM-L-6-v2`) are cached with `st.cache_resource` so they
  download once per server, not once per user.
- **Everything else** (router, rewrite, decompose, multi-query, hybrid
  retrieval, rerank, evidence-check fallback, self-correction) is the same
  logic as the original pipeline, just refactored into one function call
  per question instead of a `while True` loop.

## Files

```
repo_whisperer_app/
├── app.py             # Streamlit UI — upload, build index, chat
├── llm.py             # Groq chat wrapper (drop-in replacement for ollama.chat)
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

## 1. Get a free Groq API key

Go to **[console.groq.com](https://console.groq.com)** → sign up (no
credit card) → API Keys → Create key. Free tier as of now: 30
requests/minute, 6,000 tokens/minute — plenty for a few people testing the
app.

## 2. Run locally first (recommended)

```bash
cd repo_whisperer_app
pip install -r requirements.txt
streamlit run app.py
```

It'll open in your browser. Paste your Groq key into the sidebar field, or
put it in `.streamlit/secrets.toml` (copy `secrets.toml.example`, fill in
your key, rename to `secrets.toml` — it's git-ignored).

## 3. Deploy free on Streamlit Community Cloud

1. Push this folder to a **public GitHub repo** (e.g. `repo-whisperer-rag`).
   Make sure `.streamlit/secrets.toml` is NOT committed (it's in
   `.gitignore` already) — only commit `secrets.toml.example`.
2. Go to **[share.streamlit.io](https://share.streamlit.io)**, sign in with
   GitHub.
3. Click **"New app"**, pick your repo, branch `main`, main file path
   `app.py` (adjust if you nested the folder).
4. Before deploying (or after, in app settings), go to **Settings → Secrets**
   and paste:
   ```toml
   GROQ_API_KEY = "gsk_your_real_key_here"
   ```
   This way your friends don't need their own key — they just open the link.
5. Click **Deploy**. First build takes a few minutes (downloading
   embedding/reranker model weights). After that, share the
   `https://your-app-name.streamlit.app` link with anyone.

### If you'd rather each friend bring their own key

Skip step 4. Leave the sidebar's "Groq API key" field for users to paste
their own key into — nothing is stored server-side, it only lives in their
browser session.

## Notes / limits to expect

- **Free tier RAM** on Streamlit Community Cloud is limited (~1GB). The
  embedding + reranker models are small (~100-300MB combined) so this
  should fit, but very large PDFs (100+ pages) may be slow on first index.
- **Each user's index is in-memory only** (Chroma with no persistent
  directory) and tied to their session — refreshing the page means
  re-uploading and re-building the index. This is intentional: it keeps
  things simple and avoids one user's PDF being visible to another.
- **Groq free-tier rate limits** (30 req/min, 6k tokens/min) — the
  pipeline makes several LLM calls per question (router, rewrite, planner,
  decomposition, multi-query, evidence check, answer, verify, possibly
  self-correct), so under heavy concurrent use from multiple friends you
  may hit 429 rate-limit errors. The app surfaces these as an error message
  rather than crashing.
- If you want a stronger model, change `MODEL_MAP` in `llm.py` to map to
  `"llama-3.3-70b-versatile"` instead of `"llama-3.1-8b-instant"` (slower,
  better quality, still free tier).
