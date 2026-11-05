# Library AI Agent (with React UI)

A library assistant that runs fully on your machine. A local
[Qwen2.5-0.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct) model decides
which Python tool to call. A FastAPI backend exposes the agent, and a minimal React page
lets you chat with it. No API key is needed.

```
React UI (localhost:5173)  --HTTP-->  FastAPI (localhost:8000)  -->  agent_core.py  -->  tools.py + books.json
```

## Features

- **search_books**: find books by title, author or category and show available copies
- **reserve_book**: reserve by book ID or title; the UI shows **Confirm / Cancel** before anything is saved
- Refuses a reservation when no copies are left
- **Guardrails**: blocks requests to delete, edit or add library data, blocks attempts to
  override the agent's instructions, and checks that the customer name was typed by the user
- The UI shows which tool was used for each answer

## Project structure

```
Library_AI_Agent/
├── backend/
│   ├── agent_core.py       Agent logic: model, tool calling, guardrails
│   ├── server.py           FastAPI: POST /api/chat, POST /api/confirm, GET /api/health
│   ├── agent.py            Terminal version of the agent
│   ├── tools.py            search_books() and reserve_book()
│   ├── books.json          Book catalogue and available copies
│   ├── reservations.json   Saved reservations
│   ├── download_model.py   Downloads the model from Hugging Face
│   ├── requirements.txt
│   └── .env.example        Settings template (copy to .env)
└── frontend/               React app (Vite)
    └── src/App.jsx         Minimal chat UI (single file)
```

## Setup

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
python download_model.py        # one-time, ~1 GB, saved to backend/Models/
copy .env.example .env          # Windows (use cp on macOS/Linux)
uvicorn server:app --port 8000
```

API docs and a test page: http://localhost:8000/docs

The model weights are not stored in this repository (~940 MB, above GitHub's 100 MB limit).

### 2. Frontend (in a second terminal)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## API

| Endpoint | Body | Returns |
|---|---|---|
| `POST /api/chat` | `{"message": "Find books related to Python"}` | `reply`, `tool_used`, `books`, `needs_confirmation`, `pending` |
| `POST /api/confirm` | `{"book_id": 101, "customer_name": "Ahmed", "confirmed": true}` | `reply` with the reservation details |
| `GET /api/health` | – | `{"status": "ok"}` |

## Example questions

```
Find books related to Python
Reserve Python Crash Course for Ahmed       -> Confirm / Cancel
Reserve book 102 for Priya
Reserve To Kill a Mockingbird for Ravi      (refused: no copies left)
Delete book 101                             (blocked by guardrail)
```

## Known limitations

- Each message is handled on its own (no chat memory), so "reserve it" after a search
  does not work; name the book in the message.
- The 0.5B model is small and fast on a CPU, but it can invent details such as book IDs.
  All stock and reservation rules are enforced in Python, not by the model.
