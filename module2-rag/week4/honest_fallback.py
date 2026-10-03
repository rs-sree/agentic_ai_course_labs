"""Two questions, side by side: one the archive can answer, one it can't.
Watch the system refuse honestly instead of hallucinating - and notice the
refusal never calls the generation model at all.

Run it:  python honest_fallback.py
"""
import json

from rag.vector_store import FaissStore
from rag.bm25_store import BM25Store
from rag.answer import answer_question


def main():
    chunks = [json.loads(line) for line in open("chunks.jsonl", encoding="utf-8")]
    bm25 = BM25Store(chunks)
    faiss_store = FaissStore.load("index.faiss")

    questions = [
        "How is the city protecting taxpayers from cost overruns on the arena?",
        "How is the city handling the recent water main break on Elm Street?",
    ]
    for question in questions:
        print(f'Query: "{question}"')
        result = answer_question(question, bm25, faiss_store)
        print(f"  confidence: {result['confidence']}")
        print(f"  answer: {result['answer'][:200]}")
        print(f"  sources: {len(result['sources'])} chunk(s) cited")
        print()


if __name__ == "__main__":
    main()
