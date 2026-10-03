"""Generate a grounded, cited answer, then verify each citation against the
real source chunk it points to.

Run it:  python cite_answer.py
"""
import json

from rag.embed import embed_query
from rag.vector_store import FaissStore
from rag.bm25_store import BM25Store
from rag.hybrid import hybrid_search
from rag.reranker import rerank
from rag.generate import generate_answer


def main():
    chunks = [json.loads(line) for line in open("chunks.jsonl", encoding="utf-8")]
    bm25 = BM25Store(chunks)
    faiss_store = FaissStore.load("index.faiss")

    query = "Why did a community group sue over the arena budget, and what safeguards does the city say are already in place?"
    query_vector = embed_query(query)
    candidates = hybrid_search(query, bm25, faiss_store, query_vector, k=11, candidate_k=20)
    top_chunks = [chunk for _score, chunk in rerank(query, candidates, top_k=4)]

    print(f'Query: "{query}"\n')
    print("--- ANSWER ---")
    print(generate_answer(query, top_chunks))

    print("\n--- SOURCES (verify each citation number against the real text) ---")
    for i, chunk in enumerate(top_chunks, start=1):
        meta = chunk["metadata"]
        print(f"[{i}] {meta.get('source')} (chunk {meta.get('chunk_index')})")
        print(f"    {chunk['text'][:150].strip()}...")


if __name__ == "__main__":
    main()
