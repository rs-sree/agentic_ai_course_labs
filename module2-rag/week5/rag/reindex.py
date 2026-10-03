"""Incremental re-indexing: add or update ONE document without rebuilding
the whole Qdrant collection from scratch.
"""
from __future__ import annotations

from qdrant_client.models import Filter, FieldCondition, MatchValue

from rag.chunk import chunk_documents
from rag.embed import embed_texts
from rag.ingest import load_markdown


def _chunks_for(path):
    """Ingest + chunk ONE document, tagging chunks visibility=public by default
    (this demo's new/updated articles are all public-tier)."""
    doc = load_markdown(path)
    doc.metadata.setdefault("visibility", "public")
    chunks = chunk_documents([doc])
    out = []
    for c in chunks:
        c.metadata.setdefault("visibility", "public")
        out.append({"text": c.text, "metadata": c.metadata})
    return out


def add_document(store, path):
    """Embed and upsert a brand-new document's chunks. Touches nothing else."""
    chunk_dicts = _chunks_for(path)
    vectors = embed_texts([c["text"] for c in chunk_dicts])
    store.add(vectors, chunk_dicts)
    return len(chunk_dicts)


def update_document(store, path, source_name):
    """Remove an existing document's old chunks by source, then add its new ones."""
    store.client.delete(
        collection_name=store.collection,
        points_selector=Filter(must=[
            FieldCondition(key="metadata.source", match=MatchValue(value=source_name))
        ]),
    )
    return add_document(store, path)
