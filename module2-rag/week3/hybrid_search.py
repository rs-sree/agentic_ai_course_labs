"""Compare vector-only, keyword-only, and hybrid (RRF) search on the same
queries - one exact-ID query BM25 wins, one meaning-based query vector wins.

Run it:  python hybrid_search.py
"""
import json

from rag.embed import embed_query
from rag.vector_store import FaissStore
from rag.bm25_store import BM25Store
from rag.hybrid import hybrid_search


def show(label, results):
    print(f"  {label}:")
    for score, chunk in results[:3]:
        meta = chunk["metadata"]
        print(f"    [{score:.4f}] {meta.get('source')} chunk {meta.get('chunk_index')}")


def main():
    chunks = [json.loads(line) for line in open("chunks.jsonl", encoding="utf-8")]
    bm25 = BM25Store(chunks)
    faiss_store = FaissStore.load("index.faiss")

    queries = ["24-CV-1099", "sports venue"]

    for query in queries:
        print(f'\nQuery: "{query}"')
        query_vector = embed_query(query)

        show("vector only", faiss_store.search(query_vector, k=5))
        show("keyword only (BM25)", bm25.search(query, k=5))
        show("hybrid (RRF)", hybrid_search(query, bm25, faiss_store, query_vector, k=5))


if __name__ == "__main__":
    main()
