import streamlit as st

from loader import load_pdf
from summarizer import get_full_text, summarize_document
from chunker import chunk_documents
from bm25_search import build_bm25
from vector_store import get_embeddings, build_vector_db
from reranker import get_reranker
from qa_pipeline import answer_question

st.set_page_config(page_title="PDF Q&A", page_icon="📄", layout="wide")

st.title("📄 Upload a PDF, then ask questions.")

# ---------- Sidebar: API key + PDF upload ----------
with st.sidebar:
    st.header("Setup")

    try:
        default_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        # No secrets.toml file present at all — this is expected and fine
        # when each user is bringing their own key via the text input below.
        default_key = ""

    api_key_input = st.text_input(
        "Groq API key",
        value="",
        type="password",
        help="Get a free key at console.groq.com. Leave blank if the host already configured one.",
    )
    st.session_state["groq_api_key"] = api_key_input or default_key

    st.divider()

    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

    build_clicked = st.button("Ask", type="primary", disabled=uploaded_file is None)

    st.divider()
    if st.button("🗑️ Reset conversation"):
        st.session_state["chat_messages"] = []
        st.rerun()

# ---------- Session state ----------
for key, default in [
    ("pipeline_ready", False),
    ("chunks", None),
    ("bm25", None),
    ("db", None),
    ("summary", None),
    ("chat_messages", []),
    ("doc_name", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ---------- Build the index ----------
if build_clicked and uploaded_file is not None:
    if not st.session_state["groq_api_key"]:
        st.sidebar.error("Add a Groq API key first (console.groq.com — free).")
    else:
        with st.spinner("Reading PDF..."):
            documents = load_pdf(uploaded_file)

        with st.spinner("Summarizing document..."):
            full_text = get_full_text(documents)
            summary = summarize_document(full_text)

            chunks = chunk_documents(documents)

            bm25 = build_bm25(chunks)

            embeddings = get_embeddings()

            db = build_vector_db(chunks, embeddings)

            get_reranker()  # warms the cache

        st.session_state["chunks"] = chunks
        st.session_state["bm25"] = bm25
        st.session_state["db"] = db
        st.session_state["summary"] = summary
        st.session_state["pipeline_ready"] = True
        st.session_state["chat_messages"] = []
        st.session_state["doc_name"] = uploaded_file.name

        st.sidebar.success(f"{uploaded_file.name}")

# ---------- Main area ----------
if not st.session_state["pipeline_ready"]:
    st.info("👈 Upload a PDF and click **Ask** to get started. You'll need a free Groq API key from [console.groq.com](https://console.groq.com).")
    st.stop()

st.success(f"Ready — chatting with **{st.session_state['doc_name']}**")

with st.expander("📋 Document summary"):
    st.write(st.session_state["summary"])

# Render chat history
for msg in st.session_state["chat_messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            st.caption("Sources: " + ", ".join(f"p.{p}" for p in msg["sources"]))

# Chat input
query = st.chat_input("Ask a question about the document...")

if query:
    st.session_state["chat_messages"].append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # Build recent_history string + messages list, same shape as the notebook's `messages`
    recent_turns = st.session_state["chat_messages"][-7:-1]  # last 6 before this one
    recent_history = ""
    for msg in recent_turns:
        recent_history += f"{msg['role']}: {msg['content']}\n"

    messages_for_llm = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state["chat_messages"][:-1]
    ]

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = answer_question(
                    query=query,
                    chunks=st.session_state["chunks"],
                    bm25=st.session_state["bm25"],
                    db=st.session_state["db"],
                    summary=st.session_state["summary"],
                    reranker=get_reranker(),
                    recent_history=recent_history,
                    messages_for_llm=messages_for_llm,
                )
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                st.stop()

        if result["type"] == "summary":
            st.markdown("**Document Summary:**")
            st.write(result["content"])
        elif result["type"] == "memory":
            st.markdown("**Conversation History:**")
            st.write(result["content"] or "_No previous conversation yet._")
        else:
            st.markdown(result["content"])
            if result["sources"]:
                st.caption("Sources: " + ", ".join(f"p.{p}" for p in result["sources"]))

    st.session_state["chat_messages"].append({
        "role": "assistant",
        "content": result["content"],
        "sources": result.get("sources", []),
    })