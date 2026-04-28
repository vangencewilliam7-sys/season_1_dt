import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "knnowledge_Hub", "backend"))

from app.services.embeddings import EmbeddingService
import time

print("Testing EmbeddingService...")
embedder = EmbeddingService()
texts = ["This is a test chunk."] * 1000

print(f"Sending {len(texts)} chunks to OpenAI...")
start = time.time()
try:
    embeddings = embedder.get_embeddings_batch(texts)
    print(f"Success! Received {len(embeddings)} embeddings in {time.time() - start:.2f}s")
except Exception as e:
    print(f"Error: {e}")
