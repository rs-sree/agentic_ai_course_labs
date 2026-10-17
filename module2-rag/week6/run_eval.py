"""The retrieval + faithfulness eval harness: run the golden set through the
real answering pipeline (the exact function /ask calls), and measure how it
actually did - hit-rate, MRR, and faithfulness - instead of trusting the
three questions that happened to work in a demo.

Run it:  python run_eval.py
"""
import json

from rag.answer import answer_question
from rag.bm25_store import BM25Store
from rag.judge import judge_faithfulness
from rag.metrics import hit_rate, mean_reciprocal_rank, reciprocal_rank
from rag.vector_store import FaissStore
from eval_set import GOLDEN_SET


def main():
    chunks = [json.loads(line) for line in open("chunks.jsonl", encoding="utf-8")]
    bm25 = BM25Store(chunks)
    faiss_store = FaissStore.load("index.faiss")

    results = []
    for item in GOLDEN_SET:
        result = answer_question(item["question"], bm25, faiss_store)
        retrieved_sources = [s["source"] for s in result["sources"]]

        hr = hit_rate(retrieved_sources, item["expected_sources"])
        rr = reciprocal_rank(retrieved_sources, item["expected_sources"])

        faithful, reason = None, None
        if item["answerable"] and result["confidence"] == "high":
            sources_text = "\n\n".join(
                f"[{s['source']}]" for s in result["sources"]
            )
            faithful, reason = judge_faithfulness(result["answer"], sources_text)

        results.append({
            "id": item["id"],
            "question": item["question"],
            "answerable": item["answerable"],
            "hit_rate": hr,
            "reciprocal_rank": rr,
            "confidence": result["confidence"],
            "faithful": faithful,
            "judge_reason": reason,
        })

    print(f"{'ID':<20} {'Hit':<6} {'RR':<6} {'Conf':<6} {'Faithful':<10} Question")
    for r in results:
        hit_str = "-" if r["hit_rate"] is None else f"{r['hit_rate']:.0f}"
        rr_str = "-" if r["reciprocal_rank"] is None else f"{r['reciprocal_rank']:.2f}"
        faith_str = "-" if r["faithful"] is None else str(r["faithful"])
        print(f"{r['id']:<20} {hit_str:<6} {rr_str:<6} {r['confidence']:<6} {faith_str:<10} {r['question'][:50]}")

    retrieval_results = [r for r in results if r["hit_rate"] is not None]
    overall_hit_rate = sum(r["hit_rate"] for r in retrieval_results) / len(retrieval_results)
    overall_mrr = mean_reciprocal_rank([r["reciprocal_rank"] for r in results])
    faithful_results = [r for r in results if r["faithful"] is not None]
    faithfulness_rate = (
        sum(1 for r in faithful_results if r["faithful"]) / len(faithful_results)
        if faithful_results else 0.0
    )

    print(f"\nRetrieval hit-rate: {overall_hit_rate:.2f} ({len(retrieval_results)} retrieval questions)")
    print(f"Mean reciprocal rank: {overall_mrr:.2f}")
    print(f"Faithfulness: {faithfulness_rate:.2f} ({len(faithful_results)} answered questions judged)")

    # Save for the regression check to compare against later.
    with open("eval_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "results": results,
            "hit_rate": overall_hit_rate,
            "mrr": overall_mrr,
            "faithfulness": faithfulness_rate,
        }, f, indent=2)
    print("\nSaved eval_results.json")


if __name__ == "__main__":
    main()
