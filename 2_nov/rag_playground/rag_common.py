"""Shared helpers for the Cedarline RAG exercise (Tasks 1-4)."""
from pathlib import Path

import tiktoken

PROJECT_DIR = Path(__file__).resolve().parent
DOCS_DIR = PROJECT_DIR / "Documents"
CHROMA_DIR = PROJECT_DIR / "chroma_db"
COLLECTION_NAME = "cedarline_docs"

EMBED_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 120  # tokens
CHUNK_OVERLAP = 20  # tokens

TEST_QUESTIONS = [
    "How many annual leave days do employees receive?",
    "Which days must employees work from the office?",
    # "How quickly should a lost company laptop be reported?",
    # "How quickly are Priority 1 incidents acknowledged?"
    # "What is the company travel allowance per day?",
]

encoding = tiktoken.get_encoding("cl100k_base")


def load_documents():
    """Return {filename: text} for every .txt file in Documents/."""
    return {p.name: p.read_text(encoding="utf-8") for p in sorted(DOCS_DIR.glob("*.txt"))}


def count_tokens(text):
    return len(encoding.encode(text))


def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split text into windows of `size` tokens, each overlapping the previous by `overlap`."""
    tokens = encoding.encode(text)
    step = size - overlap
    chunks = []
    for start in range(0, len(tokens), step):
        chunks.append(encoding.decode(tokens[start:start + size]))
        if start + size >= len(tokens):
            break
    return chunks


def build_chunks():
    """Return a list of dicts: {id, source, text} for all documents."""
    records = []
    for filename, text in load_documents().items():
        for i, chunk in enumerate(chunk_text(text)):
            records.append({"id": f"{filename}::chunk{i}", "source": filename, "text": chunk})
    return records


_model = None


def get_embedder():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


def get_collection():
    import chromadb
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
        embedding_function=None,  # we supply our own embeddings
    )


def index_chunks():
    """Embed every chunk and save it (text, embedding, source filename) to ChromaDB."""
    records = build_chunks()
    embeddings = get_embedder().encode([r["text"] for r in records]).tolist()
    collection = get_collection()
    collection.upsert(
        ids=[r["id"] for r in records],
        documents=[r["text"] for r in records],
        embeddings=embeddings,
        metadatas=[{"source": r["source"]} for r in records],
    )
    return collection


def retrieve(question, k=2):
    """Return the top-k chunks as a list of {text, source, distance}."""
    collection = get_collection()
    if collection.count() == 0:
        collection = index_chunks()
    query_embedding = get_embedder().encode([question]).tolist()
    result = collection.query(query_embeddings=query_embedding, n_results=k)
    return [
        {"text": doc, "source": meta["source"], "distance": dist}
        for doc, meta, dist in zip(result["documents"][0], result["metadatas"][0], result["distances"][0])
    ]
