"""Hybrid retrieval: fuse a keyword ranking and a semantic ranking with
Reciprocal Rank Fusion (RRF) - by RANK POSITION, not raw score, so two
retrievers on completely different scales (BM25 is unbounded, cosine is
0-1) combine fairly. No training, no calibration, just rank.
"""
from __future__ import annotations


def reciprocal_rank_fusion(ranked_lists, weights=None, k=60):
    """Fuse multiple (score, chunk) ranked lists into one, by rank position.

    Each ranked_lists[i] is a list of (score, chunk) tuples, best first.
    `weights` optionally trusts one list more than another (e.g. [2, 1] to
    favor the first list two-to-one) - default is equal trust for all.
    `k` is RRF's smoothing constant (60 is the standard default) - larger k
    flattens the curve, giving lower-ranked results relatively more credit.
    """
    if weights is None:
        weights = [1.0] * len(ranked_lists)

    fused_scores = {}
    chunk_by_id = {}
    for ranked_list, weight in zip(ranked_lists, weights):
        for rank, (_score, chunk) in enumerate(ranked_list):
            chunk_id = chunk["metadata"]["chunk_id"]
            chunk_by_id[chunk_id] = chunk
            fused_scores[chunk_id] = fused_scores.get(chunk_id, 0.0) + weight / (k + rank + 1)

    ranked_ids = sorted(fused_scores, key=lambda cid: fused_scores[cid], reverse=True)
    return [(fused_scores[cid], chunk_by_id[cid]) for cid in ranked_ids]


def hybrid_search(query, bm25_store, faiss_store, query_vector, k=10, candidate_k=20, weights=None):
    """Run BM25 + vector search separately, fuse with RRF, return the top-k."""
    keyword_results = bm25_store.search(query, k=candidate_k)
    semantic_results = faiss_store.search(query_vector, k=candidate_k)
    fused = reciprocal_rank_fusion([keyword_results, semantic_results], weights=weights)
    return fused[:k]
