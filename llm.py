"""
Thin wrapper so the rest of the pipeline can call `chat(model=..., messages=...)`
exactly like it did with `ollama.chat`, but backed by Groq's hosted API
(needed because free hosting can't run a local Ollama daemon).
"""
import streamlit as st
from groq import Groq

# Maps the old Ollama model names used throughout the notebook to Groq's
# hosted equivalents. llama3.1:8B -> llama-3.1-8b-instant (fast, free-tier friendly).
MODEL_MAP = {
    "llama3.1:8b": "llama-3.1-8b-instant",
    "llama3.1:8B": "llama-3.1-8b-instant",
}


def get_client():
    # Intentionally NOT cached with @st.cache_resource: that decorator caches
    # globally across all users on the server, which would mean the first
    # user's API key gets reused for every other user. Each user brings
    # their own key via the sidebar, stored per-session in st.session_state,
    # so the client must be built fresh per call (Groq client construction
    # itself is cheap — it doesn't make a network call).
    try:
        secrets_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        # No secrets.toml file present at all — expected when every user
        # brings their own key.
        secrets_key = ""

    api_key = st.session_state.get("groq_api_key") or secrets_key
    return Groq(api_key=api_key)


def chat(model, messages):
    """Drop-in replacement for ollama.chat() — same call shape, same return shape."""
    client = get_client()
    groq_model = MODEL_MAP.get(model, model)
    completion = client.chat.completions.create(
        model=groq_model,
        messages=messages,
    )
    return {
        "message": {
            "content": completion.choices[0].message.content
        }
    }


def validate_api_key(api_key):
    try:
        client = Groq(api_key=api_key)

        client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "hi"}],
            max_tokens=1,
        )

        return True

    except Exception:
        return False