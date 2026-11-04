"""Library AI Agent: local Qwen model + search_books / reserve_book tools.

Run: python agent.py
Uses the model already downloaded in ../Models/ (no API key needed).
"""
import json
import os
import re
from pathlib import Path

import torch
from dotenv import load_dotenv
from transformers import AutoModelForCausalLM, AutoTokenizer

from tools import reserve_book, search_books

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")
MODEL_DIR = (ROOT / os.getenv("MODEL_DIR", "../Models/Qwen2.5-0.5B-Instruct")).resolve()

if not (MODEL_DIR / "config.json").is_file():
    raise SystemExit(f"Model missing at {MODEL_DIR}. First run: python ../01_download_model.py")

# STEP 2: Describe the two tools so the model knows what it can call.
# 'confirm' is not shown to the model: the agent asks the user itself.
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_books",
            "description": "Search the library by book title, author or category keyword. "
                           "Returns matching books and how many copies are available.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Title or keyword, e.g. 'python'"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reserve_book",
            "description": "Reserve a book for a customer using the book ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "book_id": {"type": "integer", "description": "Book ID, e.g. 101"},
                    "customer_name": {"type": "string", "description": "Name of the customer"},
                },
                "required": ["book_id", "customer_name"],
            },
        },
    },
]

SYSTEM_PROMPT = (
    "You are a helpful library assistant. Use search_books to find books and "
    "check availability. Use reserve_book only when the user asks to reserve a "
    "book and gives the book ID and their name. Never invent books or IDs. "
    "You cannot delete, edit or add books or reservations; politely refuse such requests."
)

# GUARDRAILS: block requests that try to change library data or override the rules
BLOCKED_PATTERNS = [
    (r"\b(delete|remove|erase|drop|clear|wipe|destroy|update|modify|edit|change|add|insert|overwrite)\b"
     r".*\b(book|books|record|records|info|information|data|details|cop(y|ies)|"
     r"reservations?|database|file|json|catalog|library)\b",
     "I can only search books and create reservations. "
     "Deleting, editing or adding library data is not allowed."),
    (r"\b(ignore|forget|disregard|override)\b.*\b(instructions?|rules?|prompt)\b"
     r"|\bsystem prompt\b|\byou are now\b",
     "I can't change my instructions. I can help you search for or reserve a book."),
]
MAX_QUESTION_LENGTH = 300
NAME_PATTERN = re.compile(r"[A-Za-z][A-Za-z .'-]{0,49}")


def check_input(question: str) -> str | None:
    """Return a refusal message if the question is not allowed, else None."""
    if len(question) > MAX_QUESTION_LENGTH:
        return f"Please keep your question under {MAX_QUESTION_LENGTH} characters."
    for pattern, refusal in BLOCKED_PATTERNS:
        if re.search(pattern, question, re.IGNORECASE):
            return refusal
    return None

# Load the DOWNLOADED model and tokenizer
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Model:", MODEL_DIR.name, "(local)")
print("Compute device:", device)

tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR), local_files_only=True)
model = AutoModelForCausalLM.from_pretrained(
    str(MODEL_DIR),
    local_files_only=True,
    dtype=torch.float16 if device.type == "cuda" else torch.float32,
)
model.to(device)
model.eval()


def generate(messages: list[dict]) -> str:
    """Send the chat + tool definitions to the model and return its reply."""
    inputs = tokenizer.apply_chat_template(
        messages,
        tools=TOOLS,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt",
        return_dict=True,
    ).to(device)

    with torch.inference_mode():
        output = model.generate(
            **inputs,
            max_new_tokens=200,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )

    new_tokens = output[0][inputs["input_ids"].shape[-1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


def parse_tool_call(reply: str) -> dict | None:
    """Return {'name': ..., 'arguments': {...}} if the model asked for a tool."""
    match = re.search(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", reply, re.DOTALL)
    if not match:
        return None
    try:
        call = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None
    if not isinstance(call.get("arguments"), dict):
        call["arguments"] = {}
    return call


def run_tool(name: str, arguments: dict) -> dict | list:
    """STEP 4: Execute the Python function the model selected."""
    try:
        if name == "search_books":
            query = str(arguments.get("query", "")).strip()
            if not query or len(query) > 100:
                return {"success": False, "message": "Please give a search word of 1-100 characters."}
            results = search_books(query)
            return results or {"message": "No matching books found."}

        if name == "reserve_book":
            book_id = arguments.get("book_id")
            customer_name = str(arguments.get("customer_name", "")).strip()
            if not NAME_PATTERN.fullmatch(customer_name):
                return {"success": False,
                        "message": "Please give a valid customer name (letters only, up to 50 characters)."}

            # First call only checks availability; nothing is saved yet
            check = reserve_book(book_id, customer_name)
            if not check.get("needs_confirmation"):
                return check

            # Ask the user before creating the reservation
            print("\nAGENT:", check["message"])
            answer = input("Confirm reservation? (yes/no): ").strip().lower()
            if answer not in ("y", "yes"):
                return {"success": False, "message": "Reservation cancelled by the user."}
            return reserve_book(book_id, customer_name, confirm=True)
    except TypeError as error:
        return {"success": False, "message": f"Bad arguments for {name}: {error}"}

    return {"success": False, "message": f"Unknown tool: {name}"}


print("\nReady! Ask about books or reserve one (exit to stop).")

# STEP 1: Accept questions from the user
while True:
    question = input("\nYou: ").strip()
    if question.lower() == "exit":
        break
    if not question:
        continue

    # GUARDRAIL: refuse blocked requests before they reach the model
    refusal = check_input(question)
    if refusal:
        print("\nAGENT:", refusal)
        continue

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    reply = generate(messages)

    # STEP 3: Did the model decide to call a tool?
    tool_call = parse_tool_call(reply)
    if tool_call is None:
        if "<tool_call>" in reply:
            reply = "Sorry, I could not understand that request. Please try rephrasing it."
        print("\nAGENT:", reply)
        continue

    name, arguments = tool_call["name"], tool_call["arguments"]
    print(f"\n[Tool selected: {name}({json.dumps(arguments)})]")

    # STEP 4: Execute the selected Python function
    result = run_tool(name, arguments)
    print("[Tool result:", json.dumps(result), "]")

    # STEP 5: Send the tool result back to the model
    messages.append({
        "role": "assistant",
        "content": "",
        "tool_calls": [{"type": "function",
                        "function": {"name": name, "arguments": arguments}}],
    })
    messages.append({"role": "tool", "name": name, "content": json.dumps(result)})
    final_reply = generate(messages)

    # STEP 6: Display the final AI response
    if parse_tool_call(final_reply) or "<tool_call>" in final_reply:
        final_reply = "Here is what I found: " + json.dumps(result)
    print("\nAGENT:", final_reply)
