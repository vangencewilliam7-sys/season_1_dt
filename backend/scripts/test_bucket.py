import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from app.services.supabase_client import SupabaseService

def test_bucket():
    db = SupabaseService()
    print("Testing Bucket Connection...")
    
    # 1. List
    files = db.list_documents()
    print(f"Files in bucket: {len(files) if isinstance(files, list) else files}")
    
    # 2. Upload test
    test_content = b"Hello from Supabase Bucket Migration Test"
    file_path = "test_upload_123.txt"
    print("Uploading test file...")
    res = db.upload_document(test_content, file_path)
    print(f"Upload result: {res}")
    
    # 3. Download test
    print("Downloading test file...")
    dl_content = db.download_document(file_path)
    print(f"Downloaded content: {dl_content}")
    assert dl_content == test_content
    
    # 4. URL Test
    print("Getting Signed URL...")
    url = db.get_document_url(file_path)
    print(f"Signed URL: {url}")
    
    print("All tests passed!")

if __name__ == "__main__":
    test_bucket()
