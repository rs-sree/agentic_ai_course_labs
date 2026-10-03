"""Build a Qdrant index with visibility metadata, so retrieval can be
filtered by who's asking - the mechanism behind access control.

Run it:  python build_secure_index.py
Prereq:  Qdrant running locally -> docker compose up -d qdrant
"""
import json

from rag.embed import embed_texts
from rag.qdrant_store import QdrantStore
from rag.access import normalize_visibility


def main():
    chunks = [json.loads(line) for line in open("chunks.jsonl", encoding="utf-8")]
    chunks = normalize_visibility(chunks)

    print(f"Loaded {len(chunks)} chunks. Embedding with OpenAI...")
    vectors = embed_texts([c["text"] for c in chunks])
    dim = len(vectors[0])

    store = QdrantStore(dim)
    store.add(vectors, chunks)
    print(f"Upserted {len(chunks)} chunks into Qdrant, every one tagged with a visibility tier.")


if __name__ == "__main__":
    main()
