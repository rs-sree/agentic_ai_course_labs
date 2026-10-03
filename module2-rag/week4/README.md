# Module 2 · Week 4 — Grounded Generation: Citations & Honest Fallbacks

The fourth stage of "The Daily Planet AI Desk" RAG pipeline: turn trustworthy retrieval into an
actual answer — grounded in real sources, cited, or honestly declined when the archive can't
support one. Everything ends up behind one real API endpoint.

## What you build
- `rag/generate.py` — `generate_answer()`: a grounded-generation wrapper around OpenAI, with two
  prompt templates (`NAIVE_PROMPT` and `GROUNDED_PROMPT`) so you can see the difference explicit
  instructions make. `format_sources()` labels chunks for citation.
- `rag/answer.py` — `answer_question()`: the full flow — retrieve, rerank, check a confidence
  threshold, then generate a cited answer or return an honest refusal.
- `grounded_answer.py` — watch a loosely-prompted model hallucinate, then fix it.
- `cite_answer.py` — a real multi-source citation, with the source text printed for verification.
- `honest_fallback.py` — an answerable question and a fabricated one, side by side.
- `app/` — the **same FastAPI service from Week 2**, extended with `POST /ask` alongside the existing
  `/health` and `/search`. Week 2's `_get_store` (FAISS only) was widened into `_get_stores` (FAISS +
  BM25, since `/ask` needs hybrid retrieval); `/search` is otherwise untouched.

## Setup
```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
Copy `.env.example` to `.env` and add your OpenAI API key (same key as Weeks 2–3). This week makes
real generation calls, not just embeddings — a few cents of usage.

## Run
```bash
python build_chunks.py            # from Week 1/3: ingest -> chunk -> chunks.jsonl (7 docs, 11 chunks)
python build_index.py             # embed the archive
python grounded_answer.py         # naive prompt hallucinates; grounded prompt doesn't
python cite_answer.py             # a real, multi-source, cited answer
python honest_fallback.py         # an answerable question vs. a fabricated one
```
For the API:
```bash
uvicorn app.main:app --port 8000
curl -X POST http://127.0.0.1:8000/ask -H "Content-Type: application/json" \
     -d '{"question": "Why did a community group sue over the arena budget?"}'
```

## Note
The confidence threshold (`CONFIDENCE_THRESHOLD = 0.0` in `rag/answer.py`) was calibrated from real
reranker scores on real in-corpus vs. out-of-corpus queries — not guessed. See the recording script's
rehearsal record for the actual numbers.

## The archive (`data/`)
The same Daily Planet corpus as Weeks 1–3, including Week 3's `arena-lawsuit-filed.md` addition.

## ⚠️ Verification status
**Fully verified for real** — real OpenAI key, real generation calls, real `uvicorn`/`curl` round-trip.
`grounded_answer.py` confirmed the naive prompt genuinely blends in outside knowledge (property/sales
tax speculation not in the sources) while the grounded prompt correctly limits itself to what's
retrieved. `cite_answer.py` produced a real multi-source cited answer with sources matching the
claims. `honest_fallback.py` confirmed the confidence gate works on real reranker scores: the
in-corpus question returned `confidence: high`, the fabricated one (a water-main break never in the
archive) correctly returned `confidence: low` and the honest refusal string. `/search` and `/ask`
verified coexisting correctly over real HTTP — same `0.6695` score as Week 2, plus a real, correctly
cited `/ask` response.
