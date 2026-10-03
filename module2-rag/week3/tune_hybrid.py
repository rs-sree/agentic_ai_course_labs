"""Tune the blend: watch how trusting keyword vs. semantic more changes the
ranking - and how over-trusting one side can re-break the very query hybrid
search was built to fix.

Run it:  python tune_hybrid.py
"""
import json

from rag.embed import embed_query
from rag.vector_store import FaissStore
from rag.bm25_store import BM25Store
from rag.hybrid import hybrid_search


def show(label, results):
    print(f"  {label}:")
    for score, chunk in results[:1]:
        meta = chunk["metadata"]
        print(f"    #1 [{score:.4f}] {meta.get('source')} chunk {meta.get('chunk_index')}")


def main():
    chunks = [json.loads(line) for line in open("chunks.jsonl", encoding="utf-8")]
    bm25 = BM25Store(chunks)
    faiss_store = FaissStore.load("index.faiss")

    print('Query: "24-CV-1099" - watch the balance tip')
    query = "24-CV-1099"
    query_vector = embed_query(query)
    show("balanced (1:1)", hybrid_search(query, bm25, faiss_store, query_vector, weights=[1, 1]))
    show("keyword-weighted (2:1)", hybrid_search(query, bm25, faiss_store, query_vector, weights=[2, 1]))
    show("heavily semantic-weighted (1:4)", hybrid_search(query, bm25, faiss_store, query_vector, weights=[1, 4]))


if __name__ == "__main__":
    main()
