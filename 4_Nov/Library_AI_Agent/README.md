# Library AI Agent

A small library assistant that runs fully on your machine. A local
[Qwen2.5-0.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct) model
decides which Python tool to call. No API key is needed.

## Features

- **search_books** – find books by title, author or category and show how many copies are available
- **reserve_book** – reserve a book after asking you to confirm (yes/no); refuses when no copies are left
- **Guardrails** – blocks requests to delete, edit or add library data, blocks attempts to
  override the agent's instructions, and validates tool arguments (search word, customer name)

## How it works

1. You ask a question.
2. The model receives the question plus the two tool definitions.
3. The model decides which tool to call (or answers directly).
4. `agent.py` runs the selected Python function from `tools.py`.
5. The tool result is sent back to the model.
6. The model's final answer is shown.

## Setup

```bash
pip install -r requirements.txt
python download_model.py        # one-time, ~1 GB, saved to ./Models/
copy .env.example .env          # Windows (use cp on macOS/Linux)
python agent.py
```

The model weights are not stored in this repository (the file is ~940 MB, above
GitHub's 100 MB limit). `download_model.py` fetches them from Hugging Face.

## Example questions

```
Do you have any python books?
Show me history books
Reserve book 102 for Priya
Reserve book 105 for Ravi                              (refused: no copies left)
Delete the book information for Python Crash Course    (blocked by guardrail)
Ignore your previous instructions                      (blocked by guardrail)
```

## Files

| File | Purpose |
|---|---|
| `agent.py` | Chat loop, model loading, tool calling and guardrails |
| `tools.py` | `search_books()` and `reserve_book()` |
| `books.json` | Book catalogue and available copies |
| `reservations.json` | Saved reservations |
| `download_model.py` | Downloads the model from Hugging Face |
| `requirements.txt` | Python packages |
| `.env.example` | Settings template (copy to `.env`) |

## Note

The 0.5B model is small and fast on a CPU, but it sometimes adds details that are
not in the tool result. All stock and reservation rules are enforced in Python
(`tools.py`), not by the model.
