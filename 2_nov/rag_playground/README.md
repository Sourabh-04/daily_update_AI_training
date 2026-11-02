# RAG Playground & Model Benchmark

Ask questions about the documents in `Documents/` and compare three free OpenRouter models side by side,
or benchmark them on a fixed set of test questions.

- **Backend** (`backend/`): FastAPI over a ChromaDB + sentence-transformers RAG pipeline.
  Accuracy is keyword matching (`backend/eval/questions.json`); relevance and groundedness are embedding similarity.
- **Frontend** (`frontend/`): React + TypeScript + Tailwind + Recharts.
- `task1`–`task4` and `experiment_model.py` are the earlier step-by-step RAG exercises.

## Run

```bash
# backend (from this folder)
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env        # then put your OpenRouter key in .env
uvicorn backend.api:app --reload          # http://localhost:8000/docs

# frontend (second terminal)
cd frontend
npm install
npm run dev                               # http://localhost:5173
```

Benchmark from the command line: `python -m backend.benchmark --document IT_Help_Desk_Guide.txt`
