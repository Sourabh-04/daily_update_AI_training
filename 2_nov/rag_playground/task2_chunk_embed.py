"""Task 2 - Chunk the documents (120 tokens, 20 overlap) and embed them."""
from rag_common import CHUNK_OVERLAP, CHUNK_SIZE, EMBED_MODEL, build_chunks, count_tokens, get_embedder

chunks = build_chunks()
print(f"Chunk size: {CHUNK_SIZE} tokens, overlap: {CHUNK_OVERLAP} tokens")
print(f"Total chunks: {len(chunks)}")
for source in sorted({c["source"] for c in chunks}):
    print(f"  {source}: {sum(c['source'] == source for c in chunks)} chunks")

sample = chunks[0]
print(f"\nSample chunk ({sample['id']}, {count_tokens(sample['text'])} tokens):")
print("-" * 80)
print(sample["text"])
print("-" * 80)

embeddings = get_embedder().encode([c["text"] for c in chunks])
print(f"\nEmbedding model: {EMBED_MODEL}")
print(f"Embeddings shape: {embeddings.shape}")
print(f"Vector size: {embeddings.shape[1]}")
