# Agentic AI Certificate — Consolidated Labs

All hands-on labs from the **BITS Pilani Digital — Professional Certificate in Agentic AI**,
organized in one place. Every lab here is the provided reference code (complete and runnable);
this folder just unifies the scattered weekly downloads into one navigable study resource.

> **How to use this:** don't just read it — run each lab, break it, change a parameter, watch what
> happens. The skill is in the doing. Each week builds on the one before.

---

## Layout

```
agentic_ai_course_labs/
├── module0-workbench/     "AI Workbench" — fundamentals bridge (progressive LLM app)
│   ├── week1/   first LLM calls + prompting
│   ├── week2/   FastAPI LLM service
│   └── week3/   Dockerized backend + Streamlit frontend (agent teaser)
└── module2-rag/           "The Daily Planet AI Desk" — a full RAG pipeline, built week by week
    ├── week2/   embeddings + vector search (FAISS → Qdrant)
    ├── week3/   hybrid search (BM25 + vector) + cross-encoder reranking
    ├── week4/   grounded generation: citations + honest fallback
    ├── week5/   access control, data freshness, managed vector DB (Pinecone)
    └── week6/   retrieval evaluation + LLM-as-judge, regression gating, Langfuse tracing
```

The RAG track is one continuous system — each week extends the same codebase and the same
newsroom corpus (`data/`). Read it in order; week N assumes week N-1.

---

## One-time setup (shared by every lab)

1. **Python 3.11+** (3.9+ works). On Windows, check "Add python.exe to PATH" during install.
2. **An OpenAI API key** — needed from the very first lab. Each lab reads it from a local `.env`.
3. **Docker Desktop** — needed for Module 0 Week 3, and the Qdrant-based RAG labs.
4. Per lab: create a venv, install deps, copy the env template.

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env      # then paste your OpenAI key into .env
```

> `.env` files were **intentionally excluded** from this consolidation (they held your real API
> key). Recreate each from the `.env.example` next to it.

---

## Module 0 — AI Workbench (fundamentals bridge)

A single text-processing service, grown from a script into a deployed app.

### Week 1 — First LLM calls & prompting
- `hello_ai.py` — your first API call to a model.
- `workbench_cli.py` — a small command-line tool around the model.
- `prompt_experiment.py` — compare prompts; results in `prompt_experiment_results.md`.
- **Concept:** what a completion is; how prompt wording changes output. Temperature, tokens.
- **Run:** `python hello_ai.py`, then `python prompt_experiment.py`.

### Week 2 — Wrap it in an API (FastAPI)
- `app/main.py`, `app/services.py`, `app/llm_client.py`, `app/models.py`.
- **Concept:** separating the LLM client from business logic; exposing it over HTTP; typed
  request/response models. This is the shape every later service reuses.
- **Run:** `uvicorn app.main:app --port 8000` → open `/docs`.

### Week 3 — Package & ship it (Docker + Streamlit)
- `backend/` (FastAPI) + `frontend/streamlit_app.py` + `docker-compose.yml`.
- `agent_teaser.py` — first taste of the agent loop (the bridge into real agentic work).
- **Concept:** containerizing a service, a UI talking to a backend, one-command spin-up.
- **Run:** `docker compose up --build` → backend `:8000`, UI `:8501`, docs `/docs`.

---

## Module 2 — RAG Systems ("The Daily Planet AI Desk")

A production-minded retrieval pipeline over a newsroom archive. The corpus (`data/articles/*.md`,
`data/wire/*.html`) grows slightly each week.

### Week 2 — Embeddings & vector search
- `rag/embed.py` — OpenAI embeddings wrapper (`embed_texts`, `embed_query`).
- `rag/vector_store.py` — `FaissStore` (cosine via `IndexFlatIP` + `normalize_L2`), save/load.
- `rag/qdrant_store.py` — same search on a real vector DB, with metadata filtering.
- `build_index.py` (offline: embed everything) · `search.py` (online: embed query → top-k).
- `app/` — FastAPI `POST /search`. **Week 4 later extends this same service.**
- **Concept:** turning text into vectors of meaning; local index vs. real vector DB.
- **Run:** `python build_chunks.py` → `python build_index.py` → `python search.py`.

### Week 3 — Hybrid search & reranking
- `rag/bm25_store.py` — keyword retrieval (BM25, no API key, no cost).
- `rag/hybrid.py` — `reciprocal_rank_fusion` + `hybrid_search` (fuse by rank, with weighting).
- `rag/reranker.py` — local cross-encoder (`ms-marco-MiniLM-L-6-v2`) re-scoring query+candidate.
- Demos: `bm25_search.py`, `hybrid_search.py`, `tune_hybrid.py`, `rerank_search.py`.
- **Concept:** semantic search misses exact names/dates/IDs — keyword search fixes that; fusing
  both then reranking gives the best precision. **The single biggest quality lever in RAG.**
- **Run:** `python hybrid_search.py`, then `python rerank_search.py`.

### Week 4 — Grounded generation: citations & honest fallbacks
- `rag/generate.py` — `generate_answer()` with `NAIVE_PROMPT` vs `GROUNDED_PROMPT`; `format_sources()`.
- `rag/answer.py` — `answer_question()`: retrieve → rerank → confidence gate → cite or refuse.
- Demos: `grounded_answer.py` (watch naive prompt hallucinate, then fix it), `cite_answer.py`,
  `honest_fallback.py` (answerable vs. fabricated question, side by side).
- `app/` — Week 2's service + `POST /ask` (hybrid retrieval behind it).
- **Concept:** grounding the model in retrieved sources, forcing citations, and refusing when the
  archive can't support an answer. This is what separates a RAG demo from a trustworthy one.
- **Run:** `python grounded_answer.py`; then `uvicorn app.main:app` and `POST /ask`.

### Week 5 — Access control, freshness & the managed path
- `rag/access.py` — `visibility_filter()` per role; `normalize_visibility()` **fails closed**
  (missing tag → most restrictive, never public).
- `rag/reindex.py` — `add_document()` / `update_document()`: upsert one doc without a full rebuild.
- `build_secure_index.py`, `access_control.py` (prove an embargoed source is invisible to `public`),
  `add_new_document.py`, `update_existing_document.py`, `pinecone_demo.py` (managed vector DB).
- **Concept:** production concerns — who can retrieve what, keeping the index current, and the
  managed-service alternative to self-hosting.
- **Run:** `docker compose up -d qdrant` → `python build_secure_index.py` → `python access_control.py`.
  (`pinecone_demo.py` needs a free `PINECONE_API_KEY`.)

### Week 6 — Retrieval evaluation, faithfulness judging & observability
- `rag/metrics.py` — `hit_rate()` / `reciprocal_rank()` / `mean_reciprocal_rank()`: did retrieval
  find the right chunk, and how high did it rank — measured against a golden set, not guessed.
- `rag/judge.py` — `judge_faithfulness()`: a second, independent model call that reads an answer
  against its sources and judges whether every claim actually holds up.
- `rag/access.py` — extended with `filter_chunks_by_role()`, so `/ask` finally respects `role`
  (public/reporter/editor), filtering candidates **before** reranking. Closes the gap Week 5's own
  README flagged: the mechanism existed, but the real endpoint ignored it.
- `eval_set.py` — a golden set of 8 real newsroom questions (incl. two deliberately hard cases: a
  genuinely out-of-corpus question and a GraphRAG-shaped multi-hop one flat retrieval can't answer).
- Demos: `run_eval.py` (score the golden set through the real `answer_question` path),
  `regression_check.py` (fail loudly if quality drops below a saved baseline), `traced_answer.py`
  (every retrieve/rerank/generate step as an inspectable Langfuse trace).
- **Concept:** prove the system is good, don't just demo it on the three questions that worked.
  Measure retrieval and faithfulness, gate regressions like a test suite, and make each stage
  observable — plus wire the Week 5 access mechanism into the actual `/ask` endpoint.
- **Run:** `python build_chunks.py` → `python build_index.py` → `python run_eval.py` →
  `python regression_check.py --save-baseline`. Tracing (`traced_answer.py`) needs the local
  Langfuse stack: `docker compose up -d` in `week6/`, or point `LANGFUSE_HOST` at Langfuse Cloud.

---

## Suggested study order

1. Module 0 Week 1 → 2 → 3  (understand the model, then how to serve it)
2. Module 2 Week 2 → 3 → 4 → 5 → 6  (build the RAG pipeline end to end, then prove it's good)

The thread that runs through all of it: **retrieval quality and grounding discipline matter more
than the model.** Week 3 (hybrid + rerank) and Week 4 (grounded + honest refusal) are the two
labs worth re-running until they're second nature; Week 6 is how you *prove* they still work.

---

## Also in your Downloads (not consolidated here)

The large `week1_code` / `week2_code` / `week3_code` zips are the instructor's `practice_demo`
apps (`app1.py`–`app4.py`, bundled `.venv` and `models/`, 24–34 MB each). They're supplementary
demos, not the graded lab code — left in place to avoid copying ~90 MB of virtualenvs and model
weights. Open them directly from `Downloads` if you want to reference them.
