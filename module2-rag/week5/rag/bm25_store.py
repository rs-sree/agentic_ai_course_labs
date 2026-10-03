"""A tiny BM25 keyword store - for exact-term retrieval that embeddings miss.

BM25 scores chunks by keyword overlap: how often the query's words appear,
discounted for repetition and normalized for chunk length. No meaning, no
training, no API calls - and unbeatable on exact names, IDs, and dates.
"""
from __future__ import annotations
import re

from rank_bm25 import BM25Okapi


def _tokenize(text):
    """Lowercase word tokens - good enough for BM25's purposes."""
    return re.findall(r"[a-z0-9]+", text.lower())


class BM25Store:
    """Holds chunks and searches them by BM25 keyword overlap."""

    def __init__(self, chunks):
        self.chunks = chunks
        corpus_tokens = [_tokenize(c["text"]) for c in chunks]
        self.bm25 = BM25Okapi(corpus_tokens)

    def search(self, query, k=3):
        scores = self.bm25.get_scores(_tokenize(query))
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        return [(float(scores[i]), self.chunks[i]) for i in ranked]
