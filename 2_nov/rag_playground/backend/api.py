"""HTTP API for the React UI.

Run from the project root:  uvicorn backend.api:app --reload
Swagger UI:                 http://localhost:8000/docs
"""
import json
import threading
from concurrent.futures import ThreadPoolExecutor

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.benchmark import LATEST_FILE, run_benchmark, save_latest
from backend.rag_service import ask_model, list_documents, load_models, retrieve
from rag_common import get_embedder

app = FastAPI(title="RAG Playground")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

get_embedder()  # load once at startup so the first request is not slow

# Latest benchmark (running, completed or failed). Only one benchmark runs at a time.
benchmark_state = json.loads(LATEST_FILE.read_text(encoding="utf-8")) if LATEST_FILE.exists() else {"status": "none"}
benchmark_lock = threading.Lock()


class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    document: str | None = None  # None = all documents
    model_ids: list[str] = Field(min_length=1, max_length=3)


class BenchmarkRequest(BaseModel):
    document: str | None = None
    model_ids: list[str] = Field(min_length=1, max_length=3)
    limit: int | None = None  # first N questions only, for cheap testing


def check_inputs(document, model_ids):
    if document is not None and document not in list_documents():
        raise HTTPException(400, f"Unknown document: {document}")
    unknown = set(model_ids) - {m["id"] for m in load_models()}
    if unknown:
        raise HTTPException(400, f"Unknown model(s): {', '.join(sorted(unknown))}")


@app.get("/documents")
def get_documents():
    return list_documents()


@app.get("/models")
def get_models():
    return load_models()


@app.post("/ask")
def ask(req: AskRequest):
    check_inputs(req.document, req.model_ids)
    hits = retrieve(req.question, document=req.document)

    def ask_one(model_id):
        try:
            answer, seconds = ask_model(model_id, req.question, hits)
            return {"model_id": model_id, "answer": answer, "latency_s": round(seconds, 3), "error": ""}
        except Exception as exc:  # one model failing must not fail the others
            return {"model_id": model_id, "answer": "", "latency_s": None, "error": f"{type(exc).__name__}: {exc}"}

    with ThreadPoolExecutor() as pool:
        answers = list(pool.map(ask_one, req.model_ids))
    return {"sources": hits, "answers": answers}


def _run(req: BenchmarkRequest):
    global benchmark_state

    def on_progress(done, total):
        benchmark_state["progress"] = {"done": done, "total": total}

    try:
        result = run_benchmark(req.model_ids, document=req.document, limit=req.limit, on_progress=on_progress)
        save_latest(result)
        benchmark_state = result
    except Exception as exc:
        benchmark_state = {"status": "failed", "error": f"{type(exc).__name__}: {exc}"}
    finally:
        benchmark_lock.release()


@app.post("/benchmark", status_code=202)
def start_benchmark(req: BenchmarkRequest, background_tasks: BackgroundTasks):
    global benchmark_state
    check_inputs(req.document, req.model_ids)
    if not benchmark_lock.acquire(blocking=False):
        raise HTTPException(409, "A benchmark is already running")
    benchmark_state = {"status": "running", "document": req.document, "model_ids": req.model_ids,
                       "progress": {"done": 0, "total": None}}
    background_tasks.add_task(_run, req)
    return {"status": "started"}


@app.get("/benchmark/latest")
def latest_benchmark():
    return benchmark_state
