import os

# Disable chromadb's anonymized telemetry BEFORE importing it. This avoids
# pulling in the opentelemetry/protobuf import chain entirely, which is
# what crashes on some environments (e.g. Streamlit Cloud) due to a
# protobuf/opentelemetry version conflict unrelated to chromadb's actual
# vector store functionality.
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import streamlit as st
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


@st.cache_resource
def get_embeddings():
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    return embeddings


def build_vector_db(chunks, embeddings):
    db = Chroma.from_documents(chunks, embeddings, collection_metadata={"hnsw:space": "cosine"})
    return db