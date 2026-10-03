"""Business logic for /search and /ask: load the archive once at startup,
then either run embedding-only search (Week 2) or the full retrieve -> rerank
-> generate/refuse flow (this week).
"""
from __future__ import annotations
import json

from rag.embed import embed_query
from rag.vector_store import FaissStore
from rag.bm25_store import BM25Store
from rag.answer import answer_question

_bm25_store = None
_faiss_store = None


def _get_stores():
    global _bm25_store, _faiss_store
    if _bm25_store is None:
        chunks = [json.loads(line) for line in open("chunks.jsonl", encoding="utf-8")]
        _bm25_store = BM25Store(chunks)
        _faiss_store = FaissStore.load("index.faiss")
    return _bm25_store, _faiss_store


def search(query: str, k: int = 3) -> list:
    """Semantic-only search - the /search route from Week 2."""
    _, faiss_store = _get_stores()
    query_vector = embed_query(query)
    results = []
    for score, chunk in faiss_store.search(query_vector, k=k):
        meta = chunk["metadata"]
        results.append({
            "score": score,
            "source": meta.get("source", ""),
            "section": meta.get("section", ""),
            "text": chunk["text"][:200],
        })
    return results


def ask(question: str) -> dict:
    """Grounded, cited, or honestly-declined answer - this week's /ask route."""
    bm25_store, faiss_store = _get_stores()
    return answer_question(question, bm25_store, faiss_store)
