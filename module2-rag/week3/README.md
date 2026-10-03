# Module 2 · Week 3 — Hybrid Search & Reranking

The third stage of "The Daily Planet AI Desk" RAG pipeline: fix semantic search's one real
blind spot — exact names, dates, and IDs — by adding keyword search, fusing it with vector
search, and reranking the results with a cross-encoder.

## What you build
- `rag/bm25_store.py` — `BM25Store`: a keyword retriever (BM25 via `rank_bm25`), no API key, no cost.
- `rag/hybrid.py` — `reciprocal_rank_fusion` and `hybrid_search`: fuse a keyword ranking and a
  semantic ranking by **rank position** (not raw score), with optional per-retriever weighting.
- `rag/reranker.py` — `rerank`: a local cross-encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2` via
  `sentence-transformers`) that reads the query and each candidate together, no API key needed.
- `bm25_search.py` — vector search vs. BM25 on an exact docket number.
- `hybrid_search.py` — vector-only vs. keyword-only vs. hybrid on two opposite query types.
- `tune_hybrid.py` — how weighting keyword vs. semantic trust changes (and can re-break) a ranking.
- `rerank_search.py` — retrieve broadly with hybrid search, then rerank precisely.

## Setup
```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
Copy `.env.example` to `.env` and add your OpenAI API key (same key as Week 2 — this week's new
reranker needs no key at all, it runs locally).

**Heaviest install of the module:** `sentence-transformers` + `torch` together are roughly
**700 MB–1 GB** the first time. This is deliberate — a local cross-encoder needs no new API key or
account, unlike the hosted alternative (e.g. Cohere Rerank).

**Python version note:** `torch==2.4.1` and `sentence-transformers==3.0.1` are pinned deliberately —
their newest releases require Python 3.10+, which would break on Python 3.9. Don't bump these
versions without re-checking Python compatibility first.

## Run
```bash
python build_chunks.py    # picks up the new arena-lawsuit-filed.md article -> 7 docs, 11 chunks
python build_index.py     # re-embeds the archive (a few more cents)
python bm25_search.py     # vector search fails on "24-CV-1099"; BM25 nails it
python hybrid_search.py   # hybrid wins both the exact-ID query and a pure-meaning query
python tune_hybrid.py     # weighting one retriever too heavily can re-break the other's win
python rerank_search.py   # a chunk buried at hybrid rank #5 jumps to reranked #1
```

## The archive (`data/`)
The same Daily Planet corpus as Weeks 1–2, plus one new article this week:
`arena-lawsuit-filed.md` — a community group suing over the arena's bond sale, docketed as
**Case No. 24-CV-1099**. It's the exact-ID example the whole week is built around.

## ⚠️ Verification status
**Fully verified for real**, real OpenAI key, twice now (originally, and re-confirmed fresh in a later
session) — every number matched exactly both times, nothing has drifted. `build_chunks.py` → 7 docs,
11 chunks. Vector search on `"24-CV-1099"` genuinely fails (wrong top result at 0.202, correct doc
buried at #2, 0.180); BM25 nails it (4.391 vs. 0.000 everywhere else). Hybrid (RRF) rescues both
opposite-blind-spot queries to #1. `tune_hybrid.py` shows over-weighting semantic search re-breaking
the exact-ID win. `rerank_search.py`: the "budget vote" query's actual-vote chunk starts buried at
hybrid rank #5 (0.0308) behind the amendments chunk at #1 (0.0328), then the cross-encoder correctly
swaps them — reranked #1 at 0.134, previous #1 dropped to -0.467.
