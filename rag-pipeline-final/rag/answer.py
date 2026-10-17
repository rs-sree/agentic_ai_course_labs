"""The full answering flow: retrieve -> filter by role -> rerank -> check
confidence -> generate or refuse. This is the logic behind the /ask endpoint.

Week 6 closes a gap Week 5's own README flagged honestly: /ask had no access
control at all, even after Week 5 built the mechanism. `role` now filters
retrieval BEFORE reranking, so a chunk the requester's role can't see never
reaches the reranker, let alone the model - the same "can't leak what it
never received" principle Week 5 taught, now actually wired into the real
endpoint, not just proven in a standalone script.
"""
from __future__ import annotations

from rag.access import filter_chunks_by_role
from rag.embed import embed_query
from rag.hybrid import hybrid_search
from rag.reranker import rerank
from rag.generate import generate_answer

CONFIDENCE_THRESHOLD = 0.0  # calibrated from real in-corpus vs out-of-corpus scores


def answer_question(question, bm25_store, faiss_store, k=4, candidate_k=20, role="public"):
    """Retrieve, filter by role, rerank, and either generate a grounded
    answer or refuse honestly. `role` defaults to "public" - the least
    access, not the most - so a caller that forgets to pass a role fails
    closed, the same discipline as an unrecognized role."""
    query_vector = embed_query(question)
    candidates = hybrid_search(question, bm25_store, faiss_store, query_vector,
                                k=candidate_k, candidate_k=candidate_k)
    candidates = filter_chunks_by_role(candidates, role)
    reranked = rerank(question, candidates, top_k=k)

    top_score = reranked[0][0] if reranked else float("-inf")
    if top_score < CONFIDENCE_THRESHOLD:
        return {
            "answer": "I can't verify that from the Daily Planet's sources.",
            "sources": [],
            "confidence": "low",
        }

    chunks = [chunk for _score, chunk in reranked]
    answer_text = generate_answer(question, chunks)
    sources = [
        {"source": c["metadata"].get("source"), "chunk_id": c["metadata"].get("chunk_id")}
        for c in chunks
    ]
    return {"answer": answer_text, "sources": sources, "confidence": "high"}
