import sys
import os
import uuid

sys.path.append(os.path.join(os.path.dirname(__file__), "knnowledge_Hub", "backend"))

from app.services.supabase_client import SupabaseService
import time

print("Testing Supabase insert...")
db = SupabaseService()

chunks = []
doc_id = str(uuid.uuid4())
for i in range(200):  # Test with 200 chunks
    chunks.append({
        "id": str(uuid.uuid4()),
        "document_id": doc_id,
        "content": "Test content " * 10,
        "embedding": [0.0] * 1536,
        "level": 0,
        "source_path": "test.pdf"
    })

print(f"Inserting {len(chunks)} chunks...")
start = time.time()
try:
    db.insert_chunks(chunks)
    print(f"Success! Inserted in {time.time() - start:.2f}s")
except Exception as e:
    print(f"Error: {e}")
