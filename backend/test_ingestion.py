import httpx
import os

def test_ingestion():
    base_url = "http://localhost:8000"
    # We use one of the existing documents in your docs folder
    file_path = r"d:\knnowledge_Hub\docs\HL_architecture.docx"
    
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    print(f"--- Starting End-to-End Ingestion Test ---")
    print(f"Target File: {os.path.basename(file_path)}")

    try:
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            response = httpx.post(f"{base_url}/api/ingest", files=files, timeout=60.0)

        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS!")
            print(f"Document ID: {result.get('document_id')}")
            print(f"Pipeline Status: {result.get('pipeline_status')}")
            print(f"\nNext Steps:")
            print(f"1. Check your Supabase 'document_chunks' table to see the parsed content.")
            print(f"2. Check the server console logs to see the Divergence and SLM Audit results.")
        else:
            print(f"Ingestion Failed (Status {response.status_code})")
            print(f"Detail: {response.text}")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_ingestion()
