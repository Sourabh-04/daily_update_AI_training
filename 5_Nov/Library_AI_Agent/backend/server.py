# FastAPI server: POST /api/chat and POST /api/confirm for the React UI
import threading

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent_core import confirm_reservation, handle_message

app = FastAPI(title="Library AI Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# One model and one set of JSON files: handle one request at a time
lock = threading.Lock()

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)


class ConfirmRequest(BaseModel):
    book_id: int
    customer_name: str = Field(min_length=1, max_length=50)
    confirmed: bool

@app.get("/api/health")
def health():
    """Quick check that the server is running."""
    return {"status": "ok"}


@app.post("/api/chat")
def chat(request: ChatRequest):
    """User sends a message; the agent searches or prepares a reservation."""
    with lock:
        return handle_message(request.message)


@app.post("/api/confirm")
def confirm(request: ConfirmRequest):
    """User clicked Confirm or Cancel for a pending reservation."""
    with lock:
        return confirm_reservation(request.book_id, request.customer_name, request.confirmed)

