"""
Documents Upload API
=====================
Exposes POST /api/documents/upload
Receives a multipart file, extracts its text, and returns it
so the frontend can inject it into the chat context.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from ..services.document_processor import DocumentProcessor

router = APIRouter()


@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Receive a clinical document, extract its text, and return:
      - filename
      - format (PDF | TXT | ...)
      - page_count
      - size_bytes
      - extracted_text   — full clinical content for the Twin to reason over
      - error            — populated if extraction partially failed
    """
    # Validate file size (max 10 MB)
    MAX_SIZE = 10 * 1024 * 1024  # 10 MB
    file_bytes = await file.read()

    if len(file_bytes) > MAX_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is 10 MB. Received {len(file_bytes) / 1024 / 1024:.1f} MB."
        )

    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Extract text
    result = DocumentProcessor.extract(file_bytes, file.filename or "upload")

    if result.get("error") and not result.get("text"):
        raise HTTPException(status_code=422, detail=result["error"])

    # Truncate to keep LLM context window manageable
    extracted_text = DocumentProcessor.truncate(result["text"], max_chars=8000)

    return {
        "filename": result["filename"],
        "format": result["format"],
        "page_count": result["page_count"],
        "size_bytes": result["size_bytes"],
        "extracted_text": extracted_text,
        "extraction_warning": result.get("error"),  # partial warnings surface here
    }
