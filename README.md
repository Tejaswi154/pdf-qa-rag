# PDF Q&A — Agentic Retrieval-Augmented Generation System

An intelligent document question-answering platform that enables users to interact with PDF documents using natural language. The system combines hybrid retrieval, query planning, reranking, evidence validation, and grounded answer generation to produce accurate, citation-backed responses.

Built using a multi-stage Agentic RAG architecture with BM25 retrieval, dense vector search, Cross-Encoder reranking, and Groq-hosted LLM inference.

---

## Key Capabilities

* Natural language question answering over PDF documents
* Hybrid retrieval using BM25 and dense vector search
* Query rewriting and decomposition for complex questions
* Multi-query retrieval for improved recall
* Cross-Encoder reranking for relevance optimization
* Evidence sufficiency validation with fallback retrieval
* Grounded answer generation with source citations
* Conversation-aware interactions
* Document summarization
* Cloud-deployable architecture with user-managed API authentication

---

## System Architecture

```text
PDF Upload
    ↓
Document Parsing
    ↓
Chunking
    ↓
Index Construction
 ┌─────────────┬─────────────┐
 │    BM25     │    FAISS    │
 └─────────────┴─────────────┘
    ↓
Agentic Query Pipeline
    ↓
Query Rewriting
    ↓
Question Decomposition
    ↓
Multi-Query Expansion
    ↓
Hybrid Retrieval
    ↓
Cross-Encoder Reranking
    ↓
Evidence Validation
    ↓
LLM Answer Generation
    ↓
Grounding Verification
    ↓
Answer + Citations
```

---

## Retrieval Pipeline

### Query Planning

User questions are rewritten into standalone retrieval-friendly queries. Complex requests are decomposed into smaller sub-questions to improve retrieval quality and coverage.

### Hybrid Search

The retrieval layer combines:

* BM25 keyword retrieval
* Dense semantic retrieval using FAISS and Sentence Transformers

This approach improves both lexical matching and semantic understanding.

### Relevance Optimization

Retrieved candidates are rescored using a Cross-Encoder reranker, ensuring that the most relevant evidence is selected before answer generation.

### Evidence Validation

The system evaluates whether sufficient supporting evidence exists before generating an answer. When evidence is weak, broader retrieval is automatically triggered.

### Grounding Verification

Generated responses are independently verified against retrieved evidence to reduce unsupported claims and hallucinations.

---

## Technology Stack

### LLM Layer

* Groq API
* Llama 3.1 8B Instant

### Retrieval Layer

* BM25
* FAISS
* Sentence Transformers

### Ranking Layer

* CrossEncoder Reranking

### Frameworks

* LangChain
* Streamlit

### Document Processing

* PyPDF
* Recursive Character Text Splitting

---

## Project Structure

```text
app.py              # Streamlit application
qa_pipeline.py      # Agentic RAG orchestration
llm.py              # Groq integration layer
loader.py           # PDF ingestion
chunker.py          # Document chunking
bm25_search.py      # Sparse retrieval
vector_store.py     # Dense retrieval (FAISS)
reranker.py         # Cross-Encoder ranking
summarizer.py       # Document summarization
```

---

## Deployment

The application is designed for cloud deployment and supports user-provided Groq API keys, allowing public access without centralized API cost management.

---

## Example Use Cases

* Enterprise document search
* Research paper analysis
* Technical documentation assistants
* Knowledge management systems
* Regulatory and compliance document review
* Internal organizational knowledge retrieval

---

## Highlights

* End-to-end Agentic RAG implementation
* Hybrid retrieval architecture
* Multi-stage relevance optimization
* Grounded answer generation
* Cloud-native deployment model
* Citation-backed responses
