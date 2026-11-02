"""Task 4 - Answer questions with an AI model (via OpenRouter) using only the retrieved chunks.

Usage: python task4_ai_answer.py ["your question"]   (no argument = run all test questions)
Requires OPENROUTER_API_KEY to be set.
"""
import sys

from backend.rag_service import ask_model, retrieve
from rag_common import TEST_QUESTIONS

# MODEL = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"
MODEL = "liquid/lfm-2.5-2.6b:free"


def answer(question):
    hits = retrieve(question, k=2)
    text, _ = ask_model(MODEL, question, hits)
    return text


if __name__ == "__main__":
    questions = [sys.argv[1]] if len(sys.argv) > 1 else TEST_QUESTIONS
    for q in questions:
        print(f"Q: {q}")
        print(f"A: {answer(q)}\n")
