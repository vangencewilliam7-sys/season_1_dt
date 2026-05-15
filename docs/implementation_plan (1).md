# Enabling Stateful Red Zone Escalations & Firewall Isolation

This plan details the technical blueprint to remediate existing routing leaks, enforce absolute domain and workflow-level isolated retrieval, implement dynamic validation nodes, and support fail-safe **Red Zone Escalations** across the five-layer digital twin hierarchy.

## User Review Required

> [!IMPORTANT]
> **Database Invalidation:** Modifying the `match_expert_dna` RPC signature in `01_init_schema.sql` is fully backwards-compatible but requires re-running the modified SQL file inside your Supabase SQL Editor to apply the enhanced query signatures.

> [!WARNING]
> **Graph State Mutations:** Adding new fields to `ChatState` (`models/chat_state.py`) changes the LangGraph payload schema. Ensure any dependent client-side parsers or UI monitors expect these enhanced diagnostic markers.

## Open Questions

> [!CAUTION]
> **External Alerts Integration:** When a query triggers a **Red Zone Escalation** (e.g., severe hemorrhage report or K+ > 6.0 mmol/L), the proposed graph node overrides standard text generation to provide immediate clinical triaging advice. Do you want this node to simultaneously fire external webhooks (e.g., SMS/Email via Twilio/SendGrid) to notify on-call staff, or should it rely strictly on dashboard/UI state rendering?

> [!NOTE]
> **Patient Mirror Mapping:** We are provisioning a new table `patient_twin_state` to store real-time user confidence indexes. Should the primary key (`patient_id`) map directly to the active session identifier, or do you have a centralized user registry table to reference?

## Proposed Changes

### Database Layer

#### [MODIFY] [01_init_schema.sql](file:///c:/Users/harin/Downloads/season_1_dt/sql_schemas/01_init_schema.sql)
- Refactor the `match_expert_dna` RPC signature to accept optional `p_domain_id` and `p_workflow_id` arguments.
- Update the internal SQL query logic to natively enforce strict `domain_id` and `workflow_id` equality matching when provisioned, isolating knowledge bases cleanly at the vector storage level.

#### [NEW] [07_patient_twin_state.sql](file:///c:/Users/harin/Downloads/season_1_dt/sql_schemas/07_patient_twin_state.sql)
- Provision the `patient_twin_state` table containing `patient_id`, `session_id`, `mirror_state` (JSONB), and update lifecycle tracking columns.

---

### Domain Adapters Layer

#### [MODIFY] [healthcare_doctor.py](file:///c:/Users/harin/Downloads/season_1_dt/backend/app/adapters/healthcare_doctor.py)
- Inject immutable clinical rule #6 enforcing mandatory priority of the Edmonton Obesity Staging System (EOSS) over basic BMI calculations during metabolic evaluations.

---

### Database Client Layer

#### [MODIFY] [supabase_client.py](file:///c:/Users/harin/Downloads/season_1_dt/backend/app/services/supabase_client.py)
- Expand `expert_vault_search()` parameters to accept an optional `workflow_id` string.
- Map and supply both `p_domain_id` and `p_workflow_id` arguments to the executed `match_expert_dna` RPC wrapper.
- Implement the `update_patient_twin_state()` operational helper method to commit live mirror dictionaries directly to Supabase.

---

### Models Layer

#### [MODIFY] [chat_state.py](file:///c:/Users/harin/Downloads/season_1_dt/backend/app/models/chat_state.py)
- Extend the `ChatState` pydantic model with extra tracking variables: `workflow_id`, `task_id`, `is_valid` (Boolean defaulting to True), and `triage_level` (String initialized to "GREEN_ZONE").

---

### Graph Nodes Layer

#### [MODIFY] [intent_detector.py](file:///c:/Users/harin/Downloads/season_1_dt/backend/app/graph/nodes/intent_detector.py)
- Refactor keywords triage logic into a robust **Multi-Tiered Classification Matrix** separating inputs into Green Zone (Standard RAG), Yellow Zone (Low Data State / Symptomatic Proxies), and Red Zone (Immediate Escalation).
- Map critical emergency identifiers directly to `intent_type = "emergency_escalation"`.

#### [MODIFY] [chat_nodes.py](file:///c:/Users/harin/Downloads/season_1_dt/backend/app/graph/nodes/chat_nodes.py)
- Update `retrieve_context_node` to extract and propagate `state.domain_id` and `state.workflow_id` parameters into the `db.expert_vault_search()` retrieval call.
- Update `reasoning_node` to output structured layer traversals alongside text logs, allowing programmatical switching of `task_id` targets.
- Implement `validation_node` verifying logic trace integrity against retrieved Master Cases.
- Refactor `generation_node` to inherit system prompt logic dynamically via `state.adapter_context['system_prompt']`.
- Implement `emergency_escalation_node` delivering pre-verified absolute clinical safety directives and bypassing custom text generation to guarantee zero hallucination risk.
- Implement `persistence_node` invoking `db.update_patient_twin_state()` to persist live mirror indices cleanly.

---

### Graph Orchestration Layer

#### [MODIFY] [chat_pipeline.py](file:///c:/Users/harin/Downloads/season_1_dt/backend/app/graph/chat_pipeline.py)
- Import and register the three new workflow nodes (`validation`, `emergency_escalation`, `persistence`).
- Update conditional path logic to support direct edge traversal to `emergency_escalation` upon encountering Red Zone triage states, and wire all exit points through the state persistence commit block.

---

### API Gateway Layer

#### [MODIFY] [chat.py](file:///c:/Users/harin/Downloads/season_1_dt/backend/app/api/chat.py)
- Introduce a deterministic **Pre-Graph Gatekeeper** layer invoking `BypassService` directly at the API ingestion boundary before instantiating or running the multi-agent graph pipeline.
- Return immediate fallback formatting when critical threshold risk limits are triggered natively.

## Verification Plan

### Automated Tests
- Execute localized endpoint validations via `pytest` or `curl` sending both standard metabolic queries and explicit Red Zone emergency statements to ensure flawless path bifurcation.
- Validate Supabase RPC match purity by querying isolated vector sets across contrasting domain spaces.

### Manual Verification
- Render the local Next.js frontend UI interface, verifying that Red Zone escalations correctly override chat bubble styling with distinct fallback badges and alerts.
- Monitor active changes in the Supabase Table view ensuring that multi-turn interaction deltas correctly populate and update persistent user mirror objects.
