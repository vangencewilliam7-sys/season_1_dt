import asyncio
import os
import sys

# Ensure backend directory is in path
sys.path.append(os.path.join(os.path.dirname(__file__), "knnowledge_Hub", "backend"))

from app.api.ingest import ingest_file
from fastapi import UploadFile
from unittest.mock import Mock

async def test():
    print("Testing ingest_file...")
    
    # Create a dummy PDF
    dummy_pdf = os.path.join(os.path.dirname(__file__), "dummy_test.pdf")
    with open(dummy_pdf, 'wb') as f:
        f.write(b'%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF')
        
    class MockUploadFile:
        def __init__(self, filename, filepath):
            self.filename = filename
            self.file = open(filepath, 'rb')
            
    mock_file = MockUploadFile("dummy_test.pdf", dummy_pdf)
    
    try:
        result = await ingest_file(mock_file)
        print("Success:", result)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(test())
