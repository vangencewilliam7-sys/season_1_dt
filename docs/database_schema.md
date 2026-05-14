# Digital Twin Database Schema

The Digital Twin's database architecture is split across two primary domains: **Knowledge Hub** tables (managed via Supabase SQL with pgvector for RAG) and **Skill Orchestration** tables (managed via SQLAlchemy for workflow/execution tracking).

---

## 1. Knowledge Hub Tables (Supabase + pgvector)

These tables form the core of the RAG pipeline, expert identity mapping, and Human-in-the-Loop (HITL) knowledge extraction.

### `document_chunks`
Stores raw ingested knowledge from uploaded PDFs/DOCX files. Preserves hierarchical structure (H1 → H2 → H3) but is considered "unverified" raw content.
- `id` (uuid, PK): Unique identifier.
- `document_id` (uuid): Source document reference.
- `content` (text): The raw chunk text.
- `parent_id` (uuid, FK): Reference back to `document_chunks(id)` for hierarchy.
- `level` (int): Hierarchy level (default: 0).
- `source_path` (text): File path of the source.
- `embedding` (vector 1536): Pgvector embedding for similarity search.
- `metadata` (jsonb): Additional attributes.
- `created_at` (timestamp): Record creation time.
- `expert_id` (uuid, Indexed): The specific expert this knowledge belongs to.

### `expert_dna`
The High-Purity Logic Vault. Contains ONLY human-verified decisions committed by the expert. This is the **only** table used for production query answers.
- `id` (uuid, PK): Unique identifier.
- `scenario_id` (text): The scenario or context identifier.
- `expert_decision` (text): The verified, final decision.
- `impact_archetype` (text): Categorization (`Safety`, `Structural`, or `Informational`).
- `industry` (text): Domain (default: `fertility`).
- `reasoning` (text): The expert's chain of reasoning.
- `embedding` (vector 1536): Pgvector embedding for semantic retrieval.
- `created_at` (timestamp): Record creation time.
- `expert_id` (uuid, Indexed): The specific expert this DNA belongs to.

### `master_cases`
Structured expert decisions extracted via the Socratic (HITL) pipeline before they are finalized into the Expert DNA vault.
- `id` (uuid, PK): Unique identifier.
- `expert_decision` (text): The extracted decision.
- `chain_of_thought` (jsonb): Detailed reasoning steps.
- `logic_tags` (text[]): Array of categorical tags.
- `confidence_note` (text): System/expert confidence assessment.
- `impact_archetype` (text): Categorization (`Safety`, `Structural`, or `Informational`).
- `source_chunk_id` (uuid, FK): Reference to the original `document_chunks(id)`.
- `scenario_id` (text): Context identifier.
- `case_embedding` (vector 1536): Pgvector embedding.
- `created_at` (timestamp): Record creation time.
- `audit_log` (jsonb): History of edits/changes (default: `[]`).
- `expert_id` (uuid, Indexed): The specific expert tied to this case.

### `pipeline_state`
LangGraph checkpoint persistence. Stores frozen graph states so experts can respond to asynchronous Socratic scenarios.
- `document_id` (uuid, PK): Primary key matching the document being processed.
- `state` (jsonb): Serialized LangGraph state.
- `status` (text): Current pipeline status (e.g., `in_progress`).
- `updated_at` (timestamp): Last updated time.

---

## 2. Skill Orchestration Tables (SQLAlchemy)

These tables handle the execution, tracking, and governance of Base and Functional Skills.

### `skill_definitions`
The central registry defining which skills are available and their operational rules.
- `id` (String, PK): Unique identifier (UUID).
- `skill_name` (String, Unique, Indexed): The skill identifier (e.g., `book_appointment`).
- `is_active` (Boolean): Guardrail toggle (if False, the LLM receives a 403 Forbidden).
- `requires_human_approval` (Boolean): Flag indicating if execution needs HITL confirmation.

### `state_ledger`
Tracks the state of long-running orchestrator workflows (Functional Skills) that might pause for human input.
- `id` (String, PK): Unique identifier (UUID).
- `workflow_id` (String, Indexed): Groups actions under a single workflow saga.
- `expert_id` (String, Indexed): The expert invoking the workflow.
- `current_state` (String): Status enum (e.g., `PENDING_EXECUTION`, `WAITING_FOR_HUMAN`).
- `updated_at` (DateTime): Last modification time.

### `execution_logs`
The immutable audit trail of every skill execution attempt (success or failure).
- `id` (String, PK): Unique identifier (UUID).
- `workflow_id` (String, Indexed): Links to the `state_ledger` or parent workflow.
- `expert_id` (String, Indexed): The expert invoking the skill.
- `skill_name` (String): The skill being executed.
- `raw_payload` (JSON): The full input payload received.
- `status` (String): Execution outcome (`PENDING`, `SUCCESS`, `FAILED`).
- `error_trace` (String, nullable): Error message or stack trace if failed.
- `created_at` (DateTime): Timestamp of the execution.
