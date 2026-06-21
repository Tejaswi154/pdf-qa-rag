from rank_bm25 import BM25Okapi


def build_bm25(chunks):
    tokenized_chunks = [
        chunk.page_content.split()
        for chunk in chunks
    ]
    bm25 = BM25Okapi(tokenized_chunks)
    return bm25
