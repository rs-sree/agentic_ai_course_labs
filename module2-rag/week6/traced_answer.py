"""The exact same answering flow as rag/answer.py, now observed end to end
with Langfuse: every retrieve/rerank/generate step becomes a real trace you
can open in a browser and inspect - what was retrieved, what the model saw,
how long each stage took, and what it cost.

Runs against a real, self-hosted Langfuse (docker compose up -d in this
folder - six services: web, worker, Postgres, ClickHouse, Redis, MinIO, the
heaviest local infrastructure this course asks for), matching "FAISS, Qdrant,
and Langfuse, all in Docker on the learner's laptop" exactly. If your machine
can't take six containers, Langfuse Cloud's free Hobby tier (50k
observations/month, no card) is a documented fallback in the README - same
code, just point LANGFUSE_HOST at https://cloud.langfuse.com instead.

Run it:  docker compose up -d          (starts Langfuse + Qdrant locally)
         python traced_answer.py
Prereq:  LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY / LANGFUSE_HOST in .env
         (already set to the local stack's auto-provisioned keys in .env.example)
"""
import json

from langfuse import get_client, observe

from rag.bm25_store import BM25Store
from rag.embed import embed_query
from rag.generate import generate_answer
from rag.hybrid import hybrid_search
from rag.judge import judge_faithfulness
from rag.reranker import rerank
from rag.vector_store import FaissStore

CONFIDENCE_THRESHOLD = 0.0


@observe(as_type="retriever")
def traced_retrieve(question, bm25_store, faiss_store, candidate_k=20):
    query_vector = embed_query(question)
    return hybrid_search(question, bm25_store, faiss_store, query_vector,
                          k=candidate_k, candidate_k=candidate_k)


@observe(as_type="span")
def traced_rerank(question, candidates, top_k=4):
    return rerank(question, candidates, top_k=top_k)


@observe(as_type="generation")
def traced_generate(question, chunks):
    return generate_answer(question, chunks)


@observe(name="answer_question")
def traced_answer_question(question, bm25_store, faiss_store):
    """Same logic as rag/answer.py's answer_question, wrapped in spans so
    each real stage - retrieve, rerank, generate - shows up as its own step
    inside one trace, instead of one opaque function call."""
    candidates = traced_retrieve(question, bm25_store, faiss_store)
    reranked = traced_rerank(question, candidates)

    top_score = reranked[0][0] if reranked else float("-inf")
    client = get_client()
    # Capture the trace ID now, while the span is still active - get_trace_url()
    # needs it explicitly once we're back in main(), after this function returns
    # and the span has already closed.
    trace_id = client.get_current_trace_id()

    if top_score < CONFIDENCE_THRESHOLD:
        client.update_current_span(output={"confidence": "low"})
        return {"answer": "I can't verify that from the Daily Planet's sources.",
                "sources": [], "confidence": "low", "trace_id": trace_id}

    chunks = [chunk for _score, chunk in reranked]
    answer_text = traced_generate(question, chunks)
    sources = [{"source": c["metadata"].get("source"),
                "chunk_id": c["metadata"].get("chunk_id")} for c in chunks]

    sources_text = "\n\n".join(f"[{s['source']}]" for s in sources)
    faithful, reason = judge_faithfulness(answer_text, sources_text)
    client.score_current_trace(name="faithfulness", value=1.0 if faithful else 0.0,
                                comment=reason)

    return {"answer": answer_text, "sources": sources, "confidence": "high", "trace_id": trace_id}


def main():
    chunks = [json.loads(line) for line in open("chunks.jsonl", encoding="utf-8")]
    bm25 = BM25Store(chunks)
    faiss_store = FaissStore.load("index.faiss")

    question = "How is the city protecting taxpayers from cost overruns on the arena?"
    result = traced_answer_question(question, bm25, faiss_store)

    print(f"Query: {question}")
    print(f"Confidence: {result['confidence']}")
    print(f"Answer: {result['answer'][:200]}")

    client = get_client()
    client.flush()
    print(f"\nView this trace: {client.get_trace_url(trace_id=result['trace_id'])}")


if __name__ == "__main__":
    main()
