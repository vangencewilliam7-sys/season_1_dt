import pytest
import httpx
import os

BASE_URL = "http://localhost:8000/api"

def test_backend_heartbeat():
    """Verify the root API is reachable."""
    try:
        response = httpx.get("http://localhost:8000/")
        assert response.status_code == 200
        assert "Knowledge Hub API" in response.json()["message"]
    except Exception as e:
        pytest.fail(f"Backend unreachable: {e}")

def test_context_loading():
    """Verify that the industry context loads correctly."""
    response = httpx.get(f"{BASE_URL}/context")
    assert response.status_code == 200
    data = response.json()
    assert "domain_name" in data
    assert "expert_role" in data
    # Default is fertility
    assert "Reproductive" in data["expert_role"]

def test_ingest_payload_validation():
    """Verify the ingestion endpoint rejects invalid file types."""
    # Create a dummy text file
    dummy_path = "test.txt"
    with open(dummy_path, "w") as f:
        f.write("test content")
    
    with open(dummy_path, "rb") as f:
        files = {'file': ('test.txt', f)}
        response = httpx.post(f"{BASE_URL}/ingest", files=files)
    
    # Assert rejection
    assert response.status_code == 400
    assert "Only .docx and .pdf files are supported" in response.json()["detail"]
    
    # Cleanup
    os.remove(dummy_path)
