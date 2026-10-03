"""Prove the gap: search for an exact docket number, vector search vs BM25.

Run it:  python bm25_search.py
Input:   chunks.jsonl (from Week 1/2) + index.faiss (from Week 2)
"""
import json

from rag.embed import embed_query
from rag.vector_store import FaissStore
from rag.bm25_store import BM25Store


def main():
    chunks = [json.loads(line) for line in open("chunks.jsonl", encoding="utf-8")]
    bm25 = BM25Store(chunks)
    faiss_store = FaissStore.load("index.faiss")

    query = "24-CV-1099"

    print(f'Query: "{query}"\n')

    print("--- VECTOR (semantic) search ---")
    query_vector = embed_query(query)
    for score, chunk in faiss_store.search(query_vector, k=5):
        meta = chunk["metadata"]
        print(f"  [{score:.3f}] {meta.get('source')} chunk {meta.get('chunk_index')}")

    print("\n--- BM25 (keyword) search ---")
    for score, chunk in bm25.search(query, k=5):
        meta = chunk["metadata"]
        print(f"  [{score:.3f}] {meta.get('source')} chunk {meta.get('chunk_index')}")


if __name__ == "__main__":
    main()
