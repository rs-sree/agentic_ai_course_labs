# AGENTS.md — working rules for this repository

> This file is instructions for an AI coding agent. (Claude Code also reads `CLAUDE.md`; this file
> is the source of truth — symlink or copy it if your tool only reads `CLAUDE.md`.)
>
> **Primary job:** when the user drops in a *new week's lab* from their Agentic AI certificate, analyze
> it against this codebase and fold its new work into the consolidated repo — code and docs — without
> breaking what's here. The full procedure is in **"Integrating a new week"** below. Read this whole
> file first, then do that.

---

## What this repository is

Consolidated hands-on labs from the **BITS Pilani Digital — Professional Certificate in Agentic AI**. Each course week ships as a self-contained folder of *complete reference code* (not stubs —
there is nothing to "fill in"). This repo unifies those weekly drops into one navigable, runnable
resource. These are **ungraded learning labs**, so running, extending, and modifying them freely is
expected and fine.

### Layout
```
agentic_ai_course_labs/
├── AGENTS.md              ← this file
├── README.md             master study guide (every week, both modules)
├── LAB-MAP.md            categorization: continuous build vs teaching demos (keep in sync)
├── module0-workbench/    Module 0 labs, as delivered (week1–3)
├── module2-rag/          Module 2 RAG labs, as delivered (week2–5, …) — the per-week drops land here
└── rag-pipeline-final/   the clean, cumulative FINAL system (latest M2 state), demos stripped
```

`rag-pipeline-final/` is the important one: it is the **continuous build** distilled — the running
product with every teaching/demo script removed. It tracks the latest Module 2 week. When a new M2
week arrives, this folder must advance to the new end state.

---

## The core mental model (do not lose this)

Every weekly lab contains three kinds of files. Classifying each new file correctly is the heart of
the integration job.

1. **Core pipeline** — the product. Lives in `rag/` (a package of modules) and `app/` (the FastAPI
   service). Files **accumulate** across weeks and existing ones get **extended**. Something always
   imports them.
2. **Pipeline runner** — a script you *invoke* to operate the system: `build_chunks.py`,
   `build_index.py`, `build_secure_index.py`. Part of the product; kept in `rag-pipeline-final/`.
3. **Teaching demo** — a standalone script that proves ONE concept (e.g. `hybrid_search.py`,
   `grounded_answer.py`, `access_control.py`). It imports the core package but **nothing imports it**.
   Demos stay in the per-week folder under `module2-rag/`; they are **NOT** copied into
   `rag-pipeline-final/`.

**The mechanical test for core vs demo** — does anything import it?
```bash
# from a week folder: is <name> imported anywhere other than its own definition?
grep -rn -E "import +<name>\b|from +<name>\b" --include=*.py . | grep -v "<name>.py:"
# empty result  -> standalone demo (leave in the week folder)
# non-empty      -> core, something depends on it (belongs in rag-pipeline-final)
```
Run it; don't guess. This is how `LAB-MAP.md`'s split was derived and it must stay the rule.

---

## Conventions observed in this codebase (match them)

When you add or modify code, mirror the existing style exactly:

- **Provider-agnostic wrappers.** LLM/embedding/rerank access is wrapped in a small module
  (`rag/embed.py`, `rag/generate.py`, `rag/reranker.py`) with a lazy singleton client
  (`_get_client()` / `_get_model()`). Keep that shape; don't scatter raw SDK calls.
- **Module docstring at the top of every file**, explaining the stage and *why* it exists — often
  one line on how the pattern generalizes to other providers. Match this teaching tone.
- **`from __future__ import annotations`** at the top; lightweight type hints; `@dataclass` for data
  holders (`Document`, `Chunk`).
- **Secrets only in `.env`**, read via `python-dotenv` + `os.getenv`. `.env.example` is the template.
  **NEVER** write a real key into any file, and never copy a `.env` into `rag-pipeline-final/` or
  commit one. If a new week needs a new key, add it to `.env.example` with a placeholder.
- **Pinned dependencies** in `requirements.txt`. When a week adds a library, append it pinned; do not
  bump existing pins unless the new week requires it (then call it out).
- **Relative paths** for artifacts (`chunks.jsonl`, `index.faiss`) — scripts assume they run from the
  project root. Preserve that.
- **Fail closed** on anything security-related (see `rag/access.py`: unknown role → least access;
  missing visibility tag → most restrictive).

---

## Integrating a new week  ← the main task

When the user gives you a new week's lab (a zip in `~/Downloads`, a folder, or a path):

1. **Place it.** Extract/copy it under the right module folder, cleaned: drop `.venv/`, `venv/`,
   `__MACOSX/`, `.DS_Store`, `__pycache__/`, bundled `models/`, and **any `.env`** (keep
   `.env.example`). For an M2 lab → `module2-rag/weekN/`. If it's a new module, create
   `moduleN-<name>/`.

2. **Diff against the current latest week.** Compare its `rag/`, `app/`, and top-level scripts with
   the newest existing week. Produce three lists:
   - **NEW core modules** (new files in `rag/`, or a new `app/` capability),
   - **MODIFIED core files** (same name, changed content — inspect the diff),
   - **NEW demos / runners** (new top-level scripts).
   Use the import test above to classify each top-level script as demo vs runner.

3. **Advance `rag-pipeline-final/`** to the new end state:
   - Copy in NEW core modules and NEW runners.
   - For MODIFIED core files, **merge carefully** — the new week usually *extends* a file
     (e.g. `app/services.py` gained `/ask` in week 4). Apply the week's changes; do not blindly
     overwrite if the final version has intentional differences. If a real conflict exists, STOP and
     show the user the conflicting sections rather than picking silently.
   - Do **not** copy demos into `rag-pipeline-final/`.
   - Merge new pinned deps into `requirements.txt`; add new keys/placeholders to `.env.example`.
   - Copy any new corpus files into `data/`.

4. **Update the docs (keep them in sync — this is not optional):**
   - `README.md` — add the new week: what it builds, key concept, how to run, how it chains on.
   - `LAB-MAP.md` — add the week's row(s): new core modules in the growth table, new demos in the
     demo table with the one idea each proves.
   - `rag-pipeline-final/README.md` — add new modules to the dependency graph and the one-line table;
     update the run steps if a new stage or key was introduced.

5. **Verify, then report.** Run the no-key smoke test to confirm nothing broke:
   ```bash
   cd rag-pipeline-final && python build_chunks.py    # must still ingest + chunk cleanly
   ```
   If the user supplies an OpenAI key, you may also run `build_index.py` and hit `/ask`. Then give the
   user a concise changelog: files added, files extended (with what changed), new deps/keys, and
   anything you flagged for their decision.

6. **Guardrails.**
   - Never overwrite the user's work or existing files without explaining what changed.
   - Never introduce a secret into tracked files.
   - If the new week contradicts an earlier design (e.g. swaps FAISS for Qdrant as the default),
     surface that as a decision for the user — don't quietly re-architect.
   - Keep edits minimal and in the existing style; you're extending a teaching codebase, not
     rewriting it.

---

## Quick reference — the final pipeline today

`rag-pipeline-final/` currently reflects **Module 2, Week 5**. Core package (12 modules):
`ingest, chunk, embed, vector_store, qdrant_store, bm25_store, hybrid, reranker, generate, answer,
access, reindex`. Service: `app/` exposing `/health` and `/ask`. Runners: `build_chunks.py`,
`build_index.py`, `build_secure_index.py`. Dependency spine:
`app/services.py → rag.answer → {embed, hybrid→(vector_store, bm25_store), reranker, generate}`.

When you finish an integration, update this section's "currently reflects" line to the new week.
