"""Business logic for the /ask endpoint: load the archive once at startup,
delegate each question to the retrieve -> rerank -> generate/refuse flow.
"""
from __future__ import annotations
import json

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


def ask(question: str, role: str = "public") -> dict:
    bm25_store, faiss_store = _get_stores()
    return answer_question(question, bm25_store, faiss_store, role=role)
