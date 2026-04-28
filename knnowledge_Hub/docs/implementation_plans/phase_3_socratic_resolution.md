# Implementation Plan — Phase 3: Socratic Resolution & HITL

The goal of Phase 3 is to bridge the gap between AI-generated scenarios and human expertise. We will introduce a **Stateful Breakpoint** in the pipeline, allowing an expert to review scenarios and provide verbal logic at their own pace.

## User Review Required

> [!IMPORTANT]
> **Interrupt Strategy**: We will use LangGraph's `interrupt()` feature. This requires a persistent "checkpointer" (we'll use a Supabase-backed checkpointer or a simple JSON state store).
> **UI Integration**: We will add a new **Knowledge Hub** page to your existing React dashboard (`js_dt/frontend`).
> **Persona Capture**: To preserve the expert's "soul" (bedside manner/tone), we will prioritize **Speech-to-Text (Whisper)** for capturing responses.

## Proposed Changes

### 1. Backend: Stateful Interrupts

#### [MODIFY] [socratic.py](file:///c:/Users/harin/Downloads/knowledge_hub/backend/app/graph/nodes/socratic.py)
Update the node to trigger a LangGraph `interrupt`. 
- Logic: "Pause here. Wait for the expert to submit a response via the `/resolve` API."

#### [NEW] [stt.py](file:///c:/Users/harin/Downloads/knowledge_hub/backend/app/services/stt.py)
A service to handle audio uploads and convert them to text using OpenAI Whisper.

#### [MODIFY] [parser.py](file:///c:/Users/harin/Downloads/knowledge_hub/backend/app/graph/nodes/parser.py)
Implement the **Structured Logic Parser**:
- Input: Expert transcript.
- Output: `MasterCase` (JSON) containing `expert_decision`, `chain_of_thought`, and `logic_tags`.
- Logic: Uses GPT-4o with strict schema enforcement to ensure the final output is deterministic.

### 2. Frontend: Social Learner UI

#### [NEW] [KnowledgeHub.jsx](file:///c:/Users/harin/Downloads/js_dt/frontend/src/pages/KnowledgeHub.jsx)
A dedicated dashboard for experts to:
1.  View pending scenarios generated in Phase 2.
2.  Listen to/read the source document context.
3.  **Record verbal responses** using a built-in mic interface.
4.  Review the STT transcript before submitting.

#### [MODIFY] [App.jsx](file:///c:/Users/harin/Downloads/js_dt/frontend/src/App.jsx)
Add the route for the new `/knowledge-hub` dashboard.

---

## Verification Plan

### Automated Tests
- `backend/tests/test_parser.py`: Feed a mock transcript and verify it produces a valid JSON `MasterCase`.
- `backend/tests/test_stt.py`: Verify connectivity with Whisper API.

### Manual Verification
1. Run the pipeline on a test doc.
2. Observe the pipeline "Pausing" at the Socratic node.
3. Open the React dashboard, record a 10-second response.
4. Verify that the pipeline resumes and correctly parses your response into the logic vault.
