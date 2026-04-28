# Implementation Plan — Phase 4 (Zero-Trust Hardening & Runtime)

This plan finalizes the system for production-grade reliability. We will implement the "Hardening" layer that ensures every piece of logic is audited and every patient/user query is safely triaged.

## User Review Required

> [!IMPORTANT]
> **Echo Verification Loop**: If the local Phi-3 auditor detects a divergence between the expert's transcript and the parsed logic, the pipeline will **re-run the parser** automatically (up to 3 times) using a deterministic temperature (0.0).
> **Emergency Bypass**: Any query matching high-risk keywords (e.g., Clinical: "bleeding", Legal: "breach") will bypass the AI entirely and alert a human expert immediately.
> **Confidence Routing**: Queries with low similarity scores (<0.75) from the vector database will be routed to a "Draft & Review" queue rather than being answered autonomously.

## Proposed Changes

### 1. LangGraph & Backend (Zero-Trust Logic)

#### [MODIFY] [pipeline.py](file:///c:/Users/harin/Downloads/knowledge_hub/backend/app/graph/pipeline.py)
- **Recursive Audit Edge**: Add a conditional edge from `audit` -> `parser` if Echo Verification fails.
- **Retry Logic**: Increment `retry_count` in the graph state to prevent infinite loops.

#### [MODIFY] [query.py](file:///c:/Users/harin/Downloads/knowledge_hub/backend/app/api/query.py)
- **Triage Layer**: Integrate `BypassService` at the start of the query flow.
- **Confidence Layer**: Implement similarity thresholding. 
    - `> 0.90`: Professional response based on expert logic.
    - `0.75 - 0.90`: Draft response for human approval.
    - `< 0.75`: Triage to human expert.

### 2. Database & Storage

#### [NEW] [expert_dna_vault.sql](file:///c:/Users/harin/Downloads/knowledge_hub/backend/supabase/migrations/expert_dna_vault.sql)
- Create a dedicated table for storing finalized, expert-verified logic (the "Expert DNA"). This ensures the runtime engine retrieves only high-purity, audited facts.

### 3. Frontend: Logic Commit Gate

#### [MODIFY] [KnowledgeHub.jsx](file:///c:/Users/harin/Downloads/js_dt/frontend/src/pages/KnowledgeHub.jsx)
- Update `handleCommit` to trigger the final save to the **Expert DNA Vault** with the chosen `Impact Archetype`.

---

## Open Questions

### 1. Expert DNA Separation
Should the verified logic be stored in a **separate table** (`expert_dna`) from the raw document chunks (`knowledge_chunks`)? I recommend separation to prevent the runtime engine from accidentally retrieving un-audited document text in high-stakes scenarios.

### 2. Bypass Notification
How should the system notify a human when the **Emergency Bypass** is triggered? (e.g., Simple API log, WebSocket alert, or email placeholder).

---

## Verification Plan

### Automated Tests
- `tests/test_audit_retry.py`: Mutate a MasterCase to force a divergence and verify the LangGraph retry loop triggers correctly.
- `tests/test_query_triage.py`: Submit high-risk and low-confidence queries and verify correct routing.

### Manual Verification
1. Run a document ingestion.
2. In the UI, commit a piece of logic.
3. Use the `/api/query` endpoint to ask a related question.
4. Verify the response is sourced from the "Expert DNA Vault."
