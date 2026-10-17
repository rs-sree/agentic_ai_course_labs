# Module 2 · Week 6 — Retrieval Evaluation & the Production RAG Capstone

The sixth and final stage of "The Daily Planet AI Desk": can you prove this system is actually
good, not just demo it on the three questions you happened to try? And, closing a real gap from
last week, does `/ask` finally respect who's asking.

## What you build
- `eval_set.py` — a golden set of 8 real questions, each with a known-correct source (or none, for
  the two deliberately hard cases: a genuinely out-of-corpus question, and a GraphRAG-shaped
  multi-hop question flat retrieval structurally can't answer).
- `rag/metrics.py` — `hit_rate()` and `reciprocal_rank()`: did retrieval find the right chunk, and
  how high did it rank, measured, not guessed.
- `rag/judge.py` — `judge_faithfulness()`: a second, independent model call that reads an answer
  against its sources and judges whether every claim actually holds up.
- `run_eval.py` — runs the golden set through the real `answer_question` pipeline (the same
  function `/ask` calls), scores it, and saves `eval_results.json`.
- `regression_check.py` — compares a fresh eval run against a saved baseline and fails loudly if
  retrieval or faithfulness got worse.
- `traced_answer.py` — the same answering flow, instrumented with Langfuse (self-hosted locally
  in Docker) so every retrieve/rerank/generate step becomes a real, inspectable trace.
- `rag/access.py` — extended with `filter_chunks_by_role()`, closing the gap Week 5's own README
  flagged: `/ask` now actually respects `role` (public/reporter/editor), filtering before
  reranking, not just proven in a standalone script.

## Setup
```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
docker compose up -d              # Qdrant (Week 5's demos) + a full local Langfuse stack
```
Copy `.env.example` to `.env` — the default values already match what `docker-compose.yml`
auto-provisions, so you don't need to sign up for anything or generate any keys yourself.

## Run
```bash
python build_chunks.py                      # ingest -> chunk -> chunks.jsonl (9 docs, 13 chunks)
python build_index.py                       # embed the archive into a FAISS index
python run_eval.py                           # score retrieval + faithfulness on the golden set
python regression_check.py --save-baseline   # first time only: save today's scores as the baseline
python regression_check.py                   # after any change: check nothing got worse
python traced_answer.py                      # same pipeline, instrumented, traces at localhost:3000
```

## Before you try Langfuse yourself: what it actually costs
- **Self-hosting Langfuse, in Docker, on your own laptop, is the primary path this lab uses.**
  `docker compose up -d` brings up six services (web, worker, Postgres, ClickHouse, Redis, MinIO)
  alongside Qdrant, and `LANGFUSE_INIT_*` env vars in `docker-compose.yml` auto-provision one
  organization, one project, and the exact API key pair already sitting in `.env.example` — no
  manual sign-up, no card, ever. It's genuinely the heaviest local infrastructure this course
  asks for, heavier than the reranker install in Week 3, and that weight is the real, honest cost
  of "runs entirely on your machine, no subscription, no data leaving your laptop."
- **If your machine can't comfortably run six extra containers**, Langfuse Cloud's free Hobby
  tier (50,000 observations/month, no credit card) is a documented fallback: sign up at
  https://cloud.langfuse.com, replace the three `LANGFUSE_*` lines in `.env` with your Cloud
  project's real keys, and set `LANGFUSE_HOST=https://cloud.langfuse.com`. Same code, same
  `traced_answer.py`, no other changes — only where the traces get stored.
- Running `traced_answer.py` without any Langfuse keys set doesn't crash anything — the client
  simply logs a warning and no-ops the tracing calls, so the RAG pipeline itself still runs and
  answers correctly. You only lose the trace, not the answer.

## The eval harness found real things, unstaged
Running the golden set against this actual code (not a hypothetical) surfaced two genuine issues,
not manufactured ones — a good reminder that an eval harness's job is to find what's actually
weak, not to confirm what already looks fine:
- **A real faithfulness failure.** One answer stated that auditors would review finances "every
  quarter," a detail the cited sources never actually said — caught automatically by
  `judge_faithfulness()`, not by a human happening to notice.
- **A real retrieval miss.** One genuinely answerable question about transit funding was wrongly
  refused, because the confidence threshold calibrated back in Week 4 doesn't perfectly generalize
  to every real query. Run `python run_eval.py` yourself and read the per-question table — both
  are visible in the real output, not asserted here.
