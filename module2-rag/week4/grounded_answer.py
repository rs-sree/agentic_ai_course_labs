"""Watch a loosely-prompted model blend in outside knowledge, then fix it
with an explicit grounding instruction.

Run it:  python grounded_answer.py
"""
import json

from rag.embed import embed_query
from rag.vector_store import FaissStore
from rag.bm25_store import BM25Store
from rag.hybrid import hybrid_search
from rag.reranker import rerank
from rag.generate import generate_answer, NAIVE_PROMPT, GROUNDED_PROMPT


def main():
    chunks = [json.loads(line) for line in open("chunks.jsonl", encoding="utf-8")]
    bm25 = BM25Store(chunks)
    faiss_store = FaissStore.load("index.faiss")

    query = "Besides the parking surcharge, what other funding sources usually pay for municipal bonds like this?"
    query_vector = embed_query(query)
    candidates = hybrid_search(query, bm25, faiss_store, query_vector, k=11, candidate_k=20)
    top_chunks = [chunk for _score, chunk in rerank(query, candidates, top_k=3)]

    print(f'Query: "{query}"\n')

    print("--- NAIVE prompt (no grounding instruction) ---")
    print(generate_answer(query, top_chunks, prompt_template=NAIVE_PROMPT))

    print("\n--- GROUNDED prompt (answer ONLY from sources) ---")
    print(generate_answer(query, top_chunks, prompt_template=GROUNDED_PROMPT))


if __name__ == "__main__":
    main()
