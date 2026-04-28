# Implementation Plan — Phase 4: Zero-Trust Defense & Production Hardening

The goal of Phase 4 is to harden the extracted logic and build the **Runtime Inference Engine**. We will implement the "Hallucination Defense Matrix" and the final "Emergency Bypass" for high-risk clinical queries.

## User Review Required

> [!WARNING]
> **Safety Overrides**: The human-in-the-loop "Impact Archetype Gate" is mandatory. No knowledge will be used by the Twin until it has been explicitly classified as Safety, Structural, or Informational by an expert.
> **Confidence Thresholds**: We will implement default thresholds (0.90 for auto-response, 0.75 for human-in-the-loop). These can be tuned later in the UI.

## Proposed Changes

### 1. Zero-Trust Verification

#### [MODIFY] [audit_node.py](file:///c:/Users/harin/Downloads/knowledge_hub/backend/app/graph/nodes/audit.py)
Implement **Echo Verification**:
- Logic: "Ask the SLM (gpt-4o-mini): Did the parsing AI change the expert's decision during logic extraction?"
- Output: Pass or Conflict.

#### [MODIFY] [pipeline.py](file:///c:/Users/harin/Downloads/knowledge_hub/backend/app/graph/pipeline.py)
Implement the **Recursive Retry (Temp 0.0)** edge:
- If Conflict → Re-run `parser_node` at Temperature 0.0 to enforce literal accuracy.
- If it fails 3 times → Trigger the **Verbal Fallback** (ask the expert to re-record via the UI).

### 2. Runtime Query Pipeline

#### [NEW] [bypass.py](file:///c:/Users/harin/Downloads/knowledge_hub/backend/app/services/bypass.py)
The **Emergency Bypass Protocol**.
- Logic: Scan incoming queries for high-risk keywords (e.g., "bleeding", "pain", "suicide").
- Action: If detected, stop the Twin and route immediately to the Doctor's priority queue.

#### [MODIFY] [query.py](file:///c:/Users/harin/Downloads/knowledge_hub/backend/app/api/query.py)
Implement the full inference logic:
1. Risk Assessment (Bypass).
2. Vector Search (pgvector).
3. Confidence Check.
4. Route to: Autonomous Response / Human Triage / Admit Uncertainty.

### 3. Final Expert Gate (UI)

#### [MODIFY] [KnowledgeHub.jsx](file:///c:/Users/harin/Downloads/js_dt/frontend/src/pages/KnowledgeHub.jsx)
Add a "Final Review" tab to the dashboard.
- Purpose: Display extracted logic and require the expert to select an **Impact Archetype**.
- Action: Commits the record to the `master_cases` table for production use.

---

## Verification Plan

### Automated Tests
- `backend/tests/test_bypass.py`: Submit a query with "Severe Pain" and verify the bypass triggers.
- `backend/tests/test_echo_verification.py`: Intentionally mutate a transcript and verify the SLM catches the logic change.

### Manual Verification
1. Finish a Socratic interview.
2. Observe the Echo Verification pass/fail in the audit log.
3. Open the "Final Review" tab on the dashboard, classify the record, and click "Commit."
4. Use the `/api/query` endpoint to see if the Twin now uses your new expert logic.
