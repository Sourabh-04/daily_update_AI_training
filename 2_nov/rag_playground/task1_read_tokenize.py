"""Task 1 - Read the documents and show the token count for each file."""
from rag_common import count_tokens, load_documents

for filename, text in load_documents().items():
    print("=" * 80)
    print(f"FILE: {filename}")
    print("=" * 80)
    print(text)
    print(f"Token count (tiktoken cl100k_base): {count_tokens(text)}\n")
