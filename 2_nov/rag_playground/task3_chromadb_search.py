"""Task 3 - Store chunks in a persistent ChromaDB and search it.

Usage: python task3_chromadb_search.py ["your question"]
"""
import sys

from rag_common import CHROMA_DIR, TEST_QUESTIONS, index_chunks, retrieve

collection = index_chunks()
print(f"Saved {collection.count()} chunks to ChromaDB at {CHROMA_DIR}\n")

question = sys.argv[1] if len(sys.argv) > 1 else TEST_QUESTIONS[0]
print(f"Question: {question}\n")
for rank, hit in enumerate(retrieve(question, k=2), start=1):
    print(f"#{rank}  source={hit['source']}  cosine distance={hit['distance']:.4f}")
    print(hit["text"])
    print("-" * 80)
