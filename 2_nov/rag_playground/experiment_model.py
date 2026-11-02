"""Compare response speed of several OpenRouter models on the test questions.

Writes:
  results/model_runs.csv     - one row per (model, question): retrieved chunk ids, time, answer
  results/model_summary.csv  - one row per model: average time to answer, ranked fastest first
"""
import csv

from backend.rag_service import ask_model, load_models, retrieve
from rag_common import PROJECT_DIR, TEST_QUESTIONS

models = [m["id"] for m in load_models()]

RESULTS_DIR = PROJECT_DIR / "results"


def main():
    RESULTS_DIR.mkdir(exist_ok=True)

    # Retrieve once per question so every model gets identical chunks.
    retrieved = {q: retrieve(q) for q in TEST_QUESTIONS}

    runs = []
    for model in models:
        print(f"\n=== {model} ===")
        for q in TEST_QUESTIONS:
            hits = retrieved[q]
            try:
                text, seconds = ask_model(model, q, hits)
                error = ""
                print(f"  [{seconds:.2f}s] {q}")
            except Exception as exc:  # free models can be unavailable or rate-limited
                text, seconds, error = "", None, f"{type(exc).__name__}: {exc}"
                print(f"  [FAILED] {q} -> {error}")
            runs.append({
                "model": model,
                "question": q,
                "retrieved_chunk_ids": ";".join(h["id"] for h in hits),
                "time_seconds": f"{seconds:.3f}" if seconds is not None else "",
                "answer": text,
                "error": error,
            })

    with open(RESULTS_DIR / "model_runs.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(runs[0]))
        writer.writeheader()
        writer.writerows(runs)

    summary = []
    for model in models:
        times = [float(r["time_seconds"]) for r in runs if r["model"] == model and r["time_seconds"]]
        summary.append({
            "model": model,
            "avg_time_seconds": f"{sum(times) / len(times):.3f}" if times else "",
            "answered": len(times),
            "failed": len(TEST_QUESTIONS) - len(times),
        })
    summary.sort(key=lambda s: float(s["avg_time_seconds"]) if s["avg_time_seconds"] else float("inf"))

    with open(RESULTS_DIR / "model_summary.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)

    print("\n=== Ranking (fastest first) ===")
    for rank, s in enumerate(summary, start=1):
        print(f"{rank}. {s['model']}  avg={s['avg_time_seconds'] or 'n/a'}s  "
              f"answered={s['answered']}  failed={s['failed']}")
    print(f"\nCSV files written to {RESULTS_DIR}")


if __name__ == "__main__":
    main()
