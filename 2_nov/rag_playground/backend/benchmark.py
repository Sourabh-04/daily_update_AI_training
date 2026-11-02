"""Benchmark models on the eval questions: one call at a time (free models rate-limit), scored and summarised.

Usage (from the project root):
  python -m backend.benchmark                                   all models, all questions
  python -m backend.benchmark --document IT_Help_Desk_Guide.txt one document's questions
  python -m backend.benchmark --limit 1                         first N questions only (cheap test)

Writes results/latest_benchmark.json (only the latest run is kept).
"""
import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from backend.rag_service import BACKEND_DIR, ask_model, load_models, retrieve
from backend.scoring import score_answer
from rag_common import PROJECT_DIR

EVAL_FILE = BACKEND_DIR / "eval" / "questions.json"
LATEST_FILE = PROJECT_DIR / "results" / "latest_benchmark.json"


def load_eval(document=None):
    """Eval items, optionally only those for one document."""
    items = json.loads(EVAL_FILE.read_text(encoding="utf-8"))
    return [i for i in items if document is None or i["document"] == document]


def _avg(values):
    values = [v for v in values if v is not None]
    return round(sum(values) / len(values), 3) if values else None


def summarise(model_ids, results, total_questions):
    """One row per model. Failed calls count as wrong; averages skip missing values."""
    summary = []
    for model_id in model_ids:
        rows = [r for r in results if r["model_id"] == model_id]
        correct = sum(r["correct"] for r in rows)
        summary.append({
            "model_id": model_id,
            "correct": correct,
            "total": total_questions,
            "accuracy": round(correct / total_questions, 3) if total_questions else None,
            "failed": sum(1 for r in rows if r["error"]),
            "avg_relevance": _avg(r["relevance"] for r in rows),
            "avg_groundedness": _avg(r["groundedness"] for r in rows),
            "avg_latency_s": _avg(r["latency_s"] for r in rows),
        })
    return summary


def run_benchmark(model_ids, document=None, limit=None, on_progress=None):
    """Run every model on every eval question and return the full result dict.

    `on_progress(done, total)` is called after each model call.
    """
    items = load_eval(document)[:limit]
    started_at = datetime.now(timezone.utc).isoformat()
    total_calls = len(items) * len(model_ids)
    done = 0

    questions, results = [], []
    for item in items:
        # Retrieve once per question so every model gets identical chunks.
        hits = retrieve(item["question"], document=item["document"])
        questions.append({
            "id": item["id"],
            "question": item["question"],
            "document": item["document"],
            "should_refuse": item["should_refuse"],
            "sources": hits,
        })
        for model_id in model_ids:
            try:
                answer, seconds = ask_model(model_id, item["question"], hits)
                error = ""
            except Exception as exc:  # free models can be unavailable or rate-limited
                answer, seconds, error = "", None, f"{type(exc).__name__}: {exc}"
            score = score_answer(item, answer, hits)
            results.append({
                "question_id": item["id"],
                "model_id": model_id,
                "answer": answer,
                "error": error,
                "latency_s": round(seconds, 3) if seconds is not None else None,
                "correct": score["correct"],
                "matched": score["matched"],
                "missing": score["missing"],
                "relevance": round(score["relevance"], 3) if score["relevance"] is not None else None,
                "groundedness": round(score["groundedness"], 3) if score["groundedness"] is not None else None,
            })
            done += 1
            if on_progress:
                on_progress(done, total_calls)

    return {
        "status": "completed",
        "document": document,
        "model_ids": model_ids,
        "started_at": started_at,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "total_questions": len(items),
        "summary": summarise(model_ids, results, len(items)),
        "questions": questions,
        "results": results,
    }


def save_latest(result, path=LATEST_FILE):
    Path(path).parent.mkdir(exist_ok=True)
    Path(path).write_text(json.dumps(result, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--document", help="only questions for this document (default: all)")
    parser.add_argument("--limit", type=int, help="only the first N questions")
    args = parser.parse_args()

    model_ids = [m["id"] for m in load_models()]
    start = time.perf_counter()
    result = run_benchmark(
        model_ids, document=args.document, limit=args.limit,
        on_progress=lambda done, total: print(f"  {done}/{total} calls done"),
    )
    save_latest(result)

    print(f"\n=== Summary ({result['total_questions']} questions, {time.perf_counter() - start:.1f}s) ===")
    for s in sorted(result["summary"], key=lambda s: -(s["accuracy"] or 0)):
        print(f"{s['model_id']}\n  accuracy={s['correct']}/{s['total']}  relevance={s['avg_relevance']}  "
              f"groundedness={s['avg_groundedness']}  latency={s['avg_latency_s']}s  failed={s['failed']}")
    print(f"\nWritten to {LATEST_FILE}")


if __name__ == "__main__":
    main()
