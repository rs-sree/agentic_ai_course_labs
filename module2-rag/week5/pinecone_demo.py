"""The same semantic search, on Pinecone's free tier - a fully managed
vector database, no Docker, no server of your own at all.

Run it:  python pinecone_demo.py
Prereq:  a free Pinecone account + API key in .env as PINECONE_API_KEY
"""
import json
import os

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

from rag.embed import embed_texts, embed_query

load_dotenv()

INDEX_NAME = "daily-planet"


def main():
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

    chunks = [json.loads(line) for line in open("chunks.jsonl", encoding="utf-8")]
    vectors = embed_texts([c["text"] for c in chunks])
    dim = len(vectors[0])

    if not pc.has_index(name=INDEX_NAME):
        pc.create_index(
            name=INDEX_NAME,
            dimension=dim,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),  # Starter/free tier region
        )

    index = pc.Index(INDEX_NAME)
    index.upsert(vectors=[
        (chunk["metadata"]["chunk_id"], vector, {"source": chunk["metadata"].get("source", "")})
        for vector, chunk in zip(vectors, chunks)
    ])
    print(f"Upserted {len(chunks)} chunks into Pinecone index '{INDEX_NAME}'.")

    query = "How will the city pay for the new sports venue?"
    query_vector = embed_query(query)

    print(f'\nQuery: "{query}"')
    results = index.query(vector=query_vector, top_k=3, include_metadata=True)
    for match in results.matches:
        print(f"  [{match.score:.3f}] {match.metadata.get('source')}")

    print("\nTear down when you're done - delete the index so nothing keeps running:")
    print(f"  pc.delete_index('{INDEX_NAME}')")


if __name__ == "__main__":
    main()
