# Implementation Plan — Phase 1: Saraswati Hub (Document Ingestion)

The goal of Phase 1 is to transform raw unstructured documents (PDFs and DOCX) into a **Hierarchical Knowledge Graph** stored in Supabase. This data will serve as the "Source of Truth" for all downstream Socratic extraction.

## User Review Required

> [!WARNING]
> **API Keys**: This implementation assumes you have filled in your `OPENAI_API_KEY` and Supabase credentials in the `backend/.env` file. I will NOT read or store these keys myself.
> **Dependency Note**: We will use `python-docx` for Word files and `pymupdf` (fitz) for PDFs.

## Proposed Changes

### 1. Database & Clients

#### [NEW] [supabase_client.py](file:///c:/Users/harin/Downloads/knowledge_hub/backend/app/services/supabase_client.py)
A wrapper to handle insertions into the `document_chunks` table and perform semantic search.

#### [NEW] [embeddings.py](file:///c:/Users/harin/Downloads/knowledge_hub/backend/app/services/embeddings.py)
A service to generate embeddings using OpenAI's `text-embedding-3-small` model.

### 2. Document Parsing logic

#### [NEW] [parser.py](file:///c:/Users/harin/Downloads/knowledge_hub/backend/app/services/parser.py)
The core logic for hierarchical decomposition.
- **DOCX**: Parse by Reading Paragraph Styles (Heading 1, Heading 2, etc.) to maintain parent-child context.
- **PDF**: Parse by detecting font sizes or structural markers (H1/H2).

### 3. Pipeline Integration

#### [MODIFY] [ingestion.py](file:///c:/Users/harin/Downloads/knowledge_hub/backend/app/graph/nodes/ingestion.py)
Update the pass-through node to actually invoke the parser and storage services.

#### [NEW] [ingest.py](file:///c:/Users/harin/Downloads/knowledge_hub/backend/app/api/ingest.py)
Implementation of the `/ingest` API endpoint to accept file uploads and trigger the LangGraph pipeline.

---

## Verification Plan

### Automated Tests
- Run `backend/tests/test_ingestion.py` (to be created) which will mock the LLM but test the structural parsing logic.
- Verify `document_chunks` table via Supabase dashboard after running an ingestion.

### Manual Verification
1. Upload `Business Overview.docx` via the API.
2. Search for "Expert Bottleneck" using a test script.
3. Confirm the hierarchy (e.g., that "The Strategic Problem" chunk identifies the "Business Overview" chunk as its parent).
