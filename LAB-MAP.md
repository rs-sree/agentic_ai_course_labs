# Lab Map — teaching demos vs. the continuous build

Every week mixes two kinds of files. Knowing which is which tells you what to *study and keep*
(the continuous system) versus what to *run once and understand* (the demos).

- **Continuous lab** — the product, built up across weeks. The `rag/` package, the `app/` API,
  and the `build_*.py` runners. Files accumulate and get extended; nothing is thrown away.
- **Teaching demo** — a standalone script that proves one concept on real data. It *imports* the
  core package but nothing imports it. Run it, see the idea, move on.
- **Pipeline runner** — part of the continuous system, but a script you *invoke* (not a module):
  `build_chunks.py`, `build_index.py`, `search.py`, `build_secure_index.py`.

---

## Module 0 — AI Workbench

| Week | Continuous build | Teaching demos |
|------|------------------|----------------|
| W1 | — (nothing carried forward yet) | `hello_ai.py`, `prompt_experiment.py`, `workbench_cli.py` |
| W2 | `app/` (FastAPI service begins) | — |
| W3 | `backend/` + `frontend/` + `docker-compose.yml` (service productionized) | `agent_teaser.py` |

**The continuous thread:** Week 1 is pure teaching (first calls, prompt experiments). The actual
product starts at Week 2 as a FastAPI service and becomes a Dockerized backend+Streamlit app in
Week 3. `agent_teaser.py` is a one-off taste of the agent loop, not part of the workbench.

---

## Module 2 — RAG ("The Daily Planet AI Desk")

### The continuous build (study + keep)

The core `rag/` package, growing each week:

| Week | New core modules | Capability added |
|------|------------------|------------------|
| W2 | `chunk, embed, ingest, vector_store, qdrant_store` | chunk → embed → vector search |
| W3 | `+ bm25_store, hybrid, reranker` | keyword + hybrid search, reranking |
| W4 | `+ generate, answer` | grounded, cited answers / honest refusal |
| W5 | `+ access, reindex` (+ `qdrant_store` returns) | access control, incremental re-index |

Carried-forward API `app/`: **W2** (adds `POST /search`) → **W3 pauses** (demo-only week) →
**W4** (extends the W2 service with `POST /ask`) → **W5** (same service).

Pipeline runners present every week: `build_chunks.py`, `build_index.py`
(+ `build_secure_index.py` in W5).

### The teaching demos (run once, understand, move on)

| Week | Demo scripts | The one idea each proves |
|------|--------------|--------------------------|
| W2 | `search.py` | query → top-k nearest chunks (the online path) |
| W2 | `qdrant_demo.py` | same search on a real vector DB + metadata filter |
| W3 | `bm25_search.py` | vector search *misses* an exact docket number; BM25 catches it |
| W3 | `hybrid_search.py` | vector-only vs keyword-only vs hybrid on opposite query types |
| W3 | `tune_hybrid.py` | weighting keyword vs semantic trust can re-break a ranking |
| W3 | `rerank_search.py` | retrieve broadly, then rerank precisely |
| W4 | `grounded_answer.py` | naive prompt hallucinates; grounded prompt doesn't |
| W4 | `cite_answer.py` | a real multi-source cited answer |
| W4 | `honest_fallback.py` | answerable vs fabricated question, side by side |
| W5 | `access_control.py` | an embargoed source is invisible to a `public` query |
| W5 | `add_new_document.py` | incremental add without a full rebuild |
| W5 | `update_existing_document.py` | update one doc's chunks in place |
| W5 | `pinecone_demo.py` | the same pipeline on a managed vector DB |

---

## How to use this split

- **To learn the system:** read the `rag/` package in week order — that's the real codebase, and
  it's small. Everything else is scaffolding around it.
- **To understand a concept:** run the matching demo for that week. Each is self-contained and
  prints a before/after you can actually see.
- **To review fast:** the demos *are* your flashcards. One script = one idea. If you can predict
  what each one prints before running it, you know the module.
