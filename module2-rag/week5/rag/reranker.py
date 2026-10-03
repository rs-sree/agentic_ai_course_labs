"""Reranking: read the query and each candidate TOGETHER (a cross-encoder),
to fix "retrieved but not relevant." Slower than retrieval, and far more
precise - which is why it only ever runs on a small shortlist, never the
whole archive.

Runs a small open cross-encoder model locally - no API key needed. The same
two-stage pattern works with a hosted API instead (e.g. Cohere Rerank):
swap what's inside `rerank()`, keep everything upstream unchanged.
"""
from __future__ import annotations

from sentence_transformers import CrossEncoder

_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
_model = None


def _get_model():
    global _model
    if _model is None:
        _model = CrossEncoder(_MODEL_NAME)
    return _model


def rerank(query, candidates, top_k=5):
    """Re-score (score, chunk) candidates by reading query+chunk together.

    `candidates` is typically a hybrid or vector search result list.
    Returns the top_k, re-ordered by the cross-encoder's score, best first.
    """
    pairs = [(query, chunk["text"]) for _score, chunk in candidates]
    cross_scores = _get_model().predict(pairs)
    reranked = sorted(zip(cross_scores, [chunk for _score, chunk in candidates]),
                       key=lambda pair: pair[0], reverse=True)
    return [(float(score), chunk) for score, chunk in reranked[:top_k]]
