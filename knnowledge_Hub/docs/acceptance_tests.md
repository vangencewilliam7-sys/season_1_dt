# Saraswati Knowledge Hub: Acceptance Test Suite

This document provides a step-by-step roadmap for verifying the full "Expert DNA" extraction pipeline. These tests solve real-world problems such as clinical hallucination, professional liability, and industry-specific jargon handling.

---

## 🚦 Testing Prerequisites
1.  **Backend**: Running at `http://localhost:8000` (`uvicorn app.main:app`)
2.  **Frontend**: Running at `http://localhost:5173` (`npm run dev`)
3.  **Local AI**: Ollama running with the `phi3` model (`ollama run phi3`)
4.  **Database**: Supabase tables and RPCs created (as per `backend/supabase/migrations`)

---

## 🟢 Easy Cases (Core Connectivity)

### 1. Ingestion Endpoint Heartbeat
*   **Real-world problem**: System downtime or API misalignment.
*   **Step**: Use Postman or `curl` to POST a dummy `.docx` file to `/api/ingest`.
*   **Expected**: `200 OK` response with a `document_id`.

### 2. Industry Context Sync
*   **Real-world problem**: Using medical terminology for a legal firm (mismatched branding/persona).
*   **Step**: Open the Dashboard and verify the sidebar title and expert role label.
*   **Expected**: Labels match the active `ContextPack` (e.g., "Medical Dosage Specialist").

### 3. Basic Vector Search
*   **Real-world problem**: Database connectivity or embedding service failure.
*   **Step**: Query `/api/query/search?query=test` with any term.
*   **Expected**: Returns at least one result (after first ingestion) with a similarity score.

---

## 🟡 Medium Cases (Pipeline Reliability)

### 4. Divergence Detection (Gap Discovery)
*   **Real-world problem**: Documents often have "soft rules" (e.g., "may consider", "if appropriate") that cause AI guessing.
*   **Step**: Upload a document containing a phrase like "The dose is usually 100mg but can vary."
*   **Expected**: The Graph should trigger the `socratic_node` and display a synthetic scenario in the dashboard.

### 5. Local Whisper Transcription
*   **Real-world problem**: Privacy of expert voice notes (no cloud STT).
*   **Step**: On a pending scenario, record a 10-second clip of your voice.
*   **Expected**: Visual confirmation of the transcript appearing locally in the dashboard without external API calls.

### 6. expert DNA Commit
*   **Real-world problem**: Losing expert knowledge because it wasn't "saved" correctly.
*   **Step**: In the **Visual Audit** tab, select an archetype (e.g., "Safety") and click commit.
*   **Expected**: The scenario moves to "Committed" status and a new record appears in the `expert_dna` database table.

### 7. Confidence-Based Routing
*   **Real-world problem**: AI being "confidently wrong" on a near-miss query.
*   **Step**: Query the twin with a term that is *conceptually similar* but not identical to your committed logic.
*   **Expected**: Response status is `human_in_the_loop` (drafted) rather than `autonomous`.

---

## 🔴 Hard Cases (Hardening & Agnosticism)

### 8. Zero-Trust Echo Verification (Audit Retry)
*   **Real-world problem**: AI hallucinations during the logic parsing phase.
*   **Step**: Provide a verbal response that is **deliberately confusing** or contradicts the source document.
*   **Expected**: The Backend should log `ECHO VERIFICATION FAILED` and triggered a **Recursive Retry** (check terminal output for retry count incrementing).

### 9. Emergency Bypass Triage
*   **Real-world problem**: Risk-critical queries (e.g., "severe bleeding") must never be handled by AI.
*   **Step**: Query `/api/query` with a high-risk keyword defined in the `ContextManager`.
*   **Expected**: Status is `emergency_bypass` and the system provides a hard-coded response to contact a human immediately.

### 10. The Industry Pivot (Legal Extraction)
*   **Real-world problem**: Building separate codebases for every industry.
*   **Step**: Change the `context_pack` in the `ContextManager` to "Legal."
*   **Expected**: 
    - Dashboard label updates to "Senior Corporate Counsel."
    - Bypass keywords transition from medical (e.g., "bleeding") to legal (e.g., "breach of contract").
    - Prompts automatically use a professional legal tone.

---

## 🔧 Verification Checklist
- [ ] All 10 tests passed?
- [ ] No private data leaked to cloud logs?
- [ ] No hallucinations detected in the Expert DNA Vault?
