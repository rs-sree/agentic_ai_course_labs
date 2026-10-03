# RAG pipeline — final system

The finished continuous build from Module 2, extracted clean: just the product, with every
teaching/demo script stripped out. This is the Week-5 end state of "The Daily Planet AI Desk" —
one runnable RAG system you can study, run, and repoint at your own data.

> Derived from `module2-rag/week5`. The per-week demos (`grounded_answer.py`, `hybrid_search.py`,
> `access_control.py`, …) were left behind on purpose — find them under `module2-rag/` if you want
> to see a single concept in isolation. Nothing here imports them.

## What's in it (the whole dependency graph)

```
app/services.py ──► rag.answer ──► rag.embed        (query → vector)
                                └► rag.hybrid ──► rag.vector_store  (FAISS, semantic)
                                │              └► rag.bm25_store    (BM25, keyword)
                                └► rag.reranker      (cross-encoder, precise re-score)
                                └► rag.generate      (grounded, cited answer / honest refusal)

build_chunks.py      ──► rag.ingest ──► rag.chunk          (docs → clean chunks)
build_index.py       ──► rag.embed  ──► rag.vector_store   (chunks → searchable index)
build_secure_index.py──► rag.qdrant_store + rag.access     (index tagged by visibility)
rag.reindex          ──► rag.chunk + rag.embed + rag.ingest (add/update one doc live)
```

Twelve small modules. That's the entire system — the rest of the course was scaffolding around
this.

## Run it end to end

```bash
python -m venv venv
venv\Scripts\activate            # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env           # paste your OpenAI key into .env
```

Local (FAISS) path:
```bash
python build_chunks.py           # ingest + chunk the corpus -> chunks.jsonl
python build_index.py            # embed -> local FAISS index
uvicorn app.main:app --port 8000 # serve /search and /ask
curl -X POST http://127.0.0.1:8000/ask -H "Content-Type: application/json" ^
     -d "{\"question\": \"Why did a community group sue over the arena budget?\"}"
```

Secure / Qdrant path (access control + live updates):
```bash
docker compose up -d qdrant
python build_secure_index.py     # index, every chunk tagged by visibility tier
```

## Repoint it at your own data

The corpus is just markdown/HTML in `data/`. To use it on something else (e.g. your ecom catalog):

1. Drop your documents into `data/` (or change the path in `rag/ingest.py`).
2. Re-run `build_chunks.py` + `build_index.py`.
3. Everything downstream — hybrid search, reranking, grounded answers — works unchanged.

That's the payoff of the continuous design: the retrieval and answer logic doesn't care what the
documents are. Swap the corpus, keep the engine.

## The modules, one line each

| Module | Role |
|--------|------|
| `rag/ingest.py` | load raw docs (markdown/HTML) into `Document` objects |
| `rag/chunk.py` | split docs into token-bounded chunks |
| `rag/embed.py` | OpenAI embeddings (`embed_texts`, `embed_query`) |
| `rag/vector_store.py` | `FaissStore` — local cosine-similarity index |
| `rag/qdrant_store.py` | `QdrantStore` — same search on a real vector DB, with filters |
| `rag/bm25_store.py` | keyword retrieval (BM25), no API key |
| `rag/hybrid.py` | reciprocal-rank-fusion of semantic + keyword |
| `rag/reranker.py` | cross-encoder re-scoring of candidates |
| `rag/generate.py` | grounded prompt → cited answer (or honest refusal) |
| `rag/answer.py` | the full flow: retrieve → rerank → confidence gate → generate |
| `rag/access.py` | per-role visibility filter; fails closed |
| `rag/reindex.py` | add/update a single document without a full rebuild |
