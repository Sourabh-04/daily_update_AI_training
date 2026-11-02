"""RAG service shared by the scripts and the API: documents, models, retrieval and model calls.

Run everything from the project root so `rag_common` is importable.
"""
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI, RateLimitError

from rag_common import DOCS_DIR, get_collection, get_embedder, index_chunks

BACKEND_DIR = Path(__file__).resolve().parent
MODELS_FILE = BACKEND_DIR / "config" / "models.json"

NOT_FOUND = "I cannot find the answer in the provided documents."
SYSTEM_PROMPT = (
    "You answer questions about Cedarline Systems using only the context provided. "
    "Do not use outside knowledge. If the context does not contain the answer, "
    f'reply exactly: "{NOT_FOUND}"'
)

load_dotenv()
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)


def load_models():
    """Model registry from config/models.json: list of {id, display_name, provider, tagline, is_open, color}."""
    return json.loads(MODELS_FILE.read_text(encoding="utf-8"))


def list_documents():
    """Filenames of the fixed documents in Documents/."""
    return [p.name for p in sorted(DOCS_DIR.glob("*.txt"))]


def retrieve(question, document=None, k=3):
    """Top-k chunks as a list of {id, text, source, distance}. `document=None` searches all documents."""
    collection = get_collection()
    if collection.count() == 0:
        collection = index_chunks()
    result = collection.query(
        query_embeddings=get_embedder().encode([question]).tolist(),
        n_results=k,
        where={"source": document} if document else None,
    )
    return [
        {"id": cid, "text": doc, "source": meta["source"], "distance": dist}
        for cid, doc, meta, dist in zip(
            result["ids"][0], result["documents"][0], result["metadatas"][0], result["distances"][0]
        )
    ]


def ask_model(model, question, hits, max_retries=5):
    """Return (answer_text, seconds). Seconds times only the successful call, not retry waits."""
    context = "\n\n".join(f"[Source: {h['source']}]\n{h['text']}" for h in hits)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"<context>\n{context}\n</context>\n\nQuestion: {question}"},
    ]
    for attempt in range(max_retries):
        try:
            start = time.perf_counter()
            response = client.chat.completions.create(model=model, messages=messages)
            seconds = time.perf_counter() - start
            return (response.choices[0].message.content or "").strip(), seconds
        except RateLimitError:
            wait = 2 ** attempt  # 1s, 2s, 4s, 8s, 16s
            print(f"  Rate limited, retrying in {wait}s...")
            time.sleep(wait)
    raise RuntimeError("All retries exhausted")
