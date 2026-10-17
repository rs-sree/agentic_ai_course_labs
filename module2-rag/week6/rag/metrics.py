"""Retrieval metrics: hit-rate and MRR - did we fetch the right chunk, and
how high did it rank, measured against a golden set instead of a guess.
"""
from __future__ import annotations


def hit_rate(retrieved_sources, expected_sources, k=None):
    """1 if any expected source appears anywhere in the retrieved list, else 0.

    `retrieved_sources` is a ranked list of source filenames (best first).
    `k` optionally limits how far down the ranked list counts as "found".
    """
    if not expected_sources:
        return None  # not a retrieval question (e.g. an out-of-corpus case)
    window = retrieved_sources[:k] if k else retrieved_sources
    return 1.0 if any(s in window for s in expected_sources) else 0.0


def reciprocal_rank(retrieved_sources, expected_sources):
    """1 / rank of the first expected source found, 0 if never found.

    Rank is 1-indexed, matching how a person would describe "it came in
    first" or "it came in third" - not the 0-indexed list position.
    """
    if not expected_sources:
        return None
    for rank, source in enumerate(retrieved_sources, start=1):
        if source in expected_sources:
            return 1.0 / rank
    return 0.0


def mean_reciprocal_rank(all_reciprocal_ranks):
    """Average reciprocal rank across every retrieval question in the set.

    None entries (non-retrieval questions, like out-of-corpus cases) are
    excluded, not treated as zero - they didn't fail retrieval, they were
    never a retrieval question to begin with.
    """
    scored = [r for r in all_reciprocal_ranks if r is not None]
    return sum(scored) / len(scored) if scored else 0.0
