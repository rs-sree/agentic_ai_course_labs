"""Access control: role-based visibility filtering for retrieval.

Extends Week 2's metadata filtering (originally used for newsroom section)
to visibility tiers. Filtering happens at the RETRIEVAL layer, before any
chunk reaches the generation model - a chunk the model never receives can't
leak, no matter what the prompt says.
"""
from __future__ import annotations

from qdrant_client.models import Filter, FieldCondition, MatchAny

# Each role can see its own tier plus everything less restrictive.
ROLE_ACCESS = {
    "public": ["public"],
    "reporter": ["public", "reporter"],
    "editor": ["public", "reporter", "editor"],
}


def visibility_filter(role):
    """Build a Qdrant filter allowing only the tiers this role can see.

    Fail closed: an unrecognized role gets the same access as "public" -
    the least, not the most.
    """
    allowed = ROLE_ACCESS.get(role, ROLE_ACCESS["public"])
    return Filter(must=[
        FieldCondition(key="metadata.visibility", match=MatchAny(any=allowed))
    ])


def filter_chunks_by_role(chunks, role):
    """Same fail-closed rule as visibility_filter, applied to a plain list of
    (score, chunk) tuples instead of a Qdrant query - for callers (like
    /ask's FAISS+BM25 hybrid pipeline) that don't query Qdrant at all.

    Filters AFTER retrieval, not at the index-query level Week 5's Qdrant
    path uses - a real, deliberate trade-off (see Week 5's own README): it
    keeps the existing hybrid+rerank pipeline intact, at the cost of
    spending retrieval compute on chunks that get thrown away afterward.
    """
    allowed = ROLE_ACCESS.get(role, ROLE_ACCESS["public"])
    return [
        (score, chunk) for score, chunk in chunks
        if chunk["metadata"].get("visibility", "editor") in allowed
    ]


def normalize_visibility(chunks):
    """Fail closed at ingestion too: a chunk with no visibility tag is
    treated as the MOST restrictive tier (editor-only), never assumed public.
    """
    for chunk in chunks:
        chunk["metadata"].setdefault("visibility", "editor")
    return chunks
