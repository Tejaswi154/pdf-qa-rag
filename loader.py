import tempfile
import os
from langchain_community.document_loaders import PyPDFLoader


def load_pdf(uploaded_file):
    """Accepts a Streamlit UploadedFile, writes it to a temp path, and loads it."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    loader = PyPDFLoader(tmp_path)
    documents = loader.load()

    os.unlink(tmp_path)
    return documents
