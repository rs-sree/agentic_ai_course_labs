# Module 2 · Week 5 — Access Control, Data Freshness & the Managed Path

The fifth stage of "The Daily Planet AI Desk" RAG pipeline: production concerns that separate a demo
from something a real newsroom would run — who sees what, whether the archive stays current, and the
managed-service alternative.

## What you build
- `rag/access.py` — `visibility_filter()`: builds a Qdrant filter restricting retrieval to whatever
  tiers a role can see. `normalize_visibility()`: any chunk missing a visibility tag defaults to
  `editor` (the most restrictive), never `public` — fail closed, not open.
- `rag/qdrant_store.py` — extended from Week 2 with `connect()` (reattach to an existing collection)
  and `search_with_filter()` (search with an arbitrary pre-built filter).
- `rag/reindex.py` — `add_document()` / `update_document()`: embed and upsert ONE document's chunks
  without rebuilding the whole index; `update_document` removes the old chunks by source first.
- `build_secure_index.py` — builds the Qdrant index with every chunk tagged by visibility.
- `access_control.py` — the same query, asked as `public`/`reporter`/`editor`, proving an embargoed
  source is invisible to a public query.
- `add_new_document.py` / `update_existing_document.py` — incremental re-indexing in action.
- `app/` — **unmodified copy of Week 4's service — see the ⚠️ gap note below.**

## Setup
```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
docker compose up -d qdrant
```
Copy `.env.example` to `.env` and add your OpenAI API key (same key as every week since Week 2). Lab 11C
also needs a free Pinecone key: sign up at https://app.pinecone.io (the Starter plan is free by default, no
card required), open the API Keys tab, and paste the key in as `PINECONE_API_KEY`.

## Run
```bash
python build_chunks.py            # ingest -> chunk -> chunks.jsonl (9 docs, 13 chunks)
python build_secure_index.py      # embed the archive into Qdrant, tagged by visibility
python access_control.py          # public/reporter/editor see different things
python add_new_document.py        # add a document without rebuilding anything else
python update_existing_document.py   # update a document's content in place
```

## The archive (`data/`)
The same Daily Planet corpus as Weeks 1–4, plus two new tiered articles staged in from the start:
- `embargoed-councilmember-conflict.md` — `visibility: editor` (an unpublished investigative draft).
- `advance-transit-vote-preview.md` — `visibility: reporter` (an advance draft, staff-only).
- The original six articles from Weeks 1–4 were each given `visibility: public` in their frontmatter.
  `newswire-arena-reaction.html` (the wire story, loaded via `load_html`, which doesn't set a
  visibility field) is the deliberate "missing tag" case — `normalize_visibility()` defaults it to
  `editor`, proving the fail-closed principle on a real chunk, not a hypothetical.
- With just these in place, `build_chunks.py` produces **9 documents, 13 chunks** — confirmed by real
  execution, matching the recording script exactly.

**`staged/` (NOT under `data/` — deliberately outside `ingest_folder`'s recursive walk):**
- `heatwave-council-response.md` — the new document for Lab 11B's incremental-add demo. Gets `cp`'d
  into `data/articles/` only as that take's own off-camera setup step, immediately before
  `add_new_document.py` runs.
- `heatwave-warning-escalated-update.md` — the replacement content for Lab 11B's update demo. Gets
  used to overwrite `data/articles/heatwave-warning.md` **in place** (same filename, same `source`
  metadata identity) immediately before `update_existing_document.py` runs.
- **Why they live outside `data/`:** `ingest_folder("data")` walks the whole `data/` tree recursively
  with no include/exclude logic. A real test run this session confirmed that if either staged file
  sits anywhere under `data/` from the start, the very first `build_chunks.py` call sweeps it in
  immediately — silently turning both of Lab 11B's marquee demos into no-ops, since the "new"/"updated"
  document would already be indexed before those takes run. See the recording script's Setup point 3
  and Rehearsal record for the full account of this bug and its fix.

## ⚠️ Gap: `app/`'s `/ask` endpoint has no access control
This week's own opening hook (Take 0) is "anyone who calls our `/ask` endpoint sees every source" —
but the fix built this week (`visibility_filter`, Qdrant metadata filtering) is only ever demonstrated
via standalone scripts (`access_control.py`) against a Qdrant collection. `app/main.py` /
`app/services.py` are an **unmodified copy of Week 4's service** — `_get_stores()` still loads the
plain `FaissStore`/`BM25Store` with no `role` parameter and no visibility filtering anywhere in the
request path. A student who finishes this lab and then calls the real, running `/ask` endpoint would
find it leaks exactly as before Week 5 started.
Fixing this for real has a genuine design question attached to it: Week 4's `/ask` retrieves via
FAISS + BM25 hybrid search (neither supports metadata filtering), while access control this week is
built on Qdrant (which does). Wiring the two together means either (a) switching `/ask`'s retrieval
backend to Qdrant with a role-aware filter, losing the hybrid+cross-encoder-rerank pipeline in its
current form, or (b) retrieving a larger FAISS/BM25 candidate set and filtering by `visibility` in
Python before reranking/generation, which keeps the current pipeline but filters after the vector
index has already been queried rather than at the index-query level the theory teaches. Neither is a
mechanical fix — **this needs an explicit decision, not a default**, before `app/` can be called done.

## ⚠️ Before you try the managed path yourself: real costs, not free-tier-everything
This week compares four ways to run retrieval. Two are genuinely free at this scale. Two are not —
know the difference before you create anything in your own AWS account.
- **FAISS / Qdrant (self-built)** — free. Runs on your own machine, no ongoing bill of any kind.
- **Pinecone** — free at this scale. The Starter tier gives 2GB of storage and over a million
  read/write operations a month, comfortably enough to hold and search this entire archive at $0.
- **AWS Bedrock Knowledge Bases** — **not free. No free tier at all.** It runs on OpenSearch
  Serverless underneath, and costs roughly **$175–350+ per month if left running.** That number starts
  the moment you create one, not when you finish using it. If you stand one up to try this yourself:
  **delete it, and confirm the OpenSearch Serverless collection underneath it is also gone,**
  immediately after you're done. Don't leave it running "to look at later."
- **AWS OpenSearch Service** (the raw, self-configured version, mentioned in this week's theory but
  not built hands-on in this lab) sits in between: a real free tier for a new account's first 12
  months, then roughly $26/month after — a fraction of Bedrock KB's cost, but still a real, ongoing
  bill if forgotten about.
- `Lab 11C` (Pinecone + Bedrock Knowledge Base) has **no code in this folder for the Bedrock half** —
  it's a live AWS console demo, not a Python script.
