# Implementation Plan: Knowledge Hub ↔ Expert Persona Integration + Skills & Retrieval

> **Goal:** Connect the two systems, implement the Skills layer, and build the full Retrieval pipeline  
> **Current Date:** 2026-04-28  
> **Project:** `season_1_dt`

---

## Current State of the Project

### Knowledge Hub (`knnowledge_Hub/`) — What's Built

| Component | Status | Location |
|---|---|---|
| FastAPI skeleton | ✅ Done | `backend/app/main.py` |
| Hierarchical Parser (Ingestion) | ✅ Done | `app/graph/nodes/ingestion.py` |
| Divergence Scanner | ✅ Done | `app/graph/nodes/divergence.py` |
| SLM Auditor | ✅ Done | `app/services/slm_auditor.py` |
| Scenario Generator | ✅ Done | `app/services/scenario_generator.py` |
| Embedding Service | ✅ Done | `app/services/embeddings.py` |
| Supabase Client | ✅ Done | `app/services/supabase_client.py` |
| STT Service | ✅ Done | `app/services/stt.py` |
| Parser Node (Structured Output) | ✅ Done | `app/graph/nodes/parser.py` |
| Audit Node (Echo Verification) | ✅ Done | `app/graph/nodes/audit.py` |
| Socratic Node (HITL Breakpoint) | ✅ Done | `app/services/scenario_generator.py` |
| LangGraph Pipeline | ✅ Done | `app/graph/pipeline.py` |
| `/api/ingest` endpoint | ✅ Done | `app/api/ingest.py` |
| `/api/query` endpoint | ✅ Done | `app/api/query.py` |
| Context Manager | ✅ Done | `app/services/context_manager.py` |
| Bypass (Emergency) | ✅ Done | `app/services/bypass.py` |
| Supabase migrations | ⚠️ Partial | `backend/supabase/` |
| Frontend (Social Learner UI) | 🔲 Not Started | `frontend/` |
| Master Cases generation loop | ⚠️ Partial | Built in pipeline but loop trigger not automated |
| Implicit knowledge continuous loop | ⚠️ Partial | Logic exists, automation missing |

---

### Expert Persona (`Expert-Persona-/`) — What's Built

| Component | Status | Location |
|---|---|---|
| `PersonaManifest` schema (Pydantic) | ✅ Done | `core/schemas.py` |
| `ExtractionState` (LangGraph TypedDict) | ✅ Done | `core/schemas.py` |
| `IngestionNode` | ✅ Done | `core/nodes/ingestion_node.py` |
| `JournalistNode` | ✅ Done | `core/nodes/journalist_node.py` |
| `AnswerProcessorNode` | ✅ Done | `core/nodes/answer_processor_node.py` |
| `CompilerNode` | ✅ Done | `core/nodes/compiler_node.py` |
| `RendererNode` | ✅ Done | `core/renderer.py` |
| LangGraph pipeline + HITL pause | ✅ Done | `core/graph.py` |
| `DomainAdapter` abstract base | ✅ Done | `adapters/base_adapter.py` |
| `GenericAdapter` | ✅ Done | `adapters/_reference_impl/` |
| `RecruitingAdapter` | ✅ Done | `adapters/recruiting/` |
| `HealthcareAdapter` | ✅ Done | `adapters/healthcare/` |
| `TechConsultingAdapter` | ✅ Done | `adapters/tech_consulting/` |
| `BaseDocumentReader` + `FilesystemReader` | ✅ Done | `runtime/readers/` |
| `APIReader` | ✅ Done | `runtime/readers/api_reader.py` |
| `SQLReader` | ✅ Done | `runtime/readers/sql_reader.py` |
| `SupabaseReader` | ✅ Done | `runtime/readers/supabase_reader.py` |
| `EmbeddingService` | ✅ Done | `runtime/services/embedding_service.py` |
| `KnowledgeVaultService` | ✅ Done | `runtime/services/knowledge_vault.py` |
| `/extract/start` + `/extract/status` API | ✅ Done | `runtime/api/extraction.py` |
| `/shadow/pending` + `/shadow/approve` API | ✅ Done | `runtime/api/shadow.py` |
| Shadow Mode dashboard (static HTML) | ✅ Done | `runtime/static/` |
| Phase 1 tests (15 passing) | ✅ Done | `tests/` |
| Phase 2 adapter tests (24 passing) | ✅ Done | `tests/` |
| **KB ↔ Persona connection** | 🔲 **Not built** | — |
| **Skills Layer** | 🔲 **Not built** | — |
| **Runtime Retrieval Pipeline** | 🔲 **Not built** | — |
| **Full Digital Twin chat endpoint** | 🔲 **Not built** | — |

---

## What Needs to Be Built (The 3 Remaining Phases)

---

## Phase 3 — Connect Knowledge Hub ↔ Expert Persona

> **Goal:** The Persona framework reads real data from the Knowledge Hub and generates a `PersonaManifest` from actual expert content

### The Connection Contract

The `SupabaseReader` (already built in `Expert-Persona-/backend/runtime/readers/supabase_reader.py`) is the bridge. It needs to be pointed at the Knowledge Hub's Supabase tables:

```python
# The connection is already coded — we just need to wire the table names

# Knowledge Hub writes to:
#   - document_chunks (with hierarchy, embeddings)
#   - master_cases (expert decisions)

# Expert Persona's SupabaseReader reads from:
#   - document_chunks  → maps to Document objects
#   - master_cases     → maps to Document objects (with special metadata)
```

### Tasks: Phase 3

#### 3.1 — Audit & Align Supabase Schema

- [ ] Check Knowledge Hub Supabase migrations for exact table names + column names
- [ ] Check `SupabaseReader` in Expert Persona for expected schema
- [ ] Write an alignment document: KH columns ↔ SupabaseReader field mapping
- [ ] If schema mismatches: decide where to fix (add a view in Supabase, or update SupabaseReader)

#### 3.2 — `.env` Bridge

Both services need to share credentials:

- [ ] Confirm `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are set in both `.env` files
- [ ] Add to Expert Persona `.env`:
  ```env
  READER_TYPE=supabase
  SUPABASE_KH_CHUNKS_TABLE=document_chunks
  SUPABASE_KH_CASES_TABLE=master_cases
  ```
- [ ] Update `SupabaseReader` to use configurable table names (not hardcoded)

#### 3.3 — Integration Test: KB → Persona

- [ ] Write `tests/test_kb_integration.py`:
  - Start an extraction with `reader_type="supabase"` for a real `expert_id`
  - Assert: `documents` list is non-empty
  - Assert: `behavioral_hypotheses` are generated from real KB content
  - Assert: `generated_questions` are domain-appropriate
- [ ] Run with `pytest tests/test_kb_integration.py -v`

#### 3.4 — End-to-End Extraction Test

- [ ] Pick a real expert (one with documents in the Knowledge Hub)
- [ ] Trigger extraction via `POST /extract/start`
  ```json
  {
    "expert_id": "<uuid>",
    "domain": "healthcare",
    "reader_type": "supabase"
  }
  ```
- [ ] Review generated questions via the Shadow Mode dashboard
- [ ] Submit expert answers
- [ ] Verify `PersonaManifest` is generated and stored
- [ ] **Milestone:** First real `PersonaManifest` generated from real KB data ✅

---

## Phase 4 — Skills Layer

> **Goal:** Build the two-tier skill architecture (Base Skills + Functional Skills) that the Digital Twin uses to take actions

### Design

```
skills/
├── base/                        # Infrastructure-level capabilities
│   ├── base_skill.py            # Abstract base class
│   ├── email_skill.py           # "Send an email"
│   ├── message_skill.py         # "Send a message/notification"
│   ├── search_skill.py          # "Search the knowledge base"
│   └── draft_skill.py           # "Draft a document/response"
│
└── functional/                  # Expert-contextualized executions
    ├── functional_skill.py      # Abstract base class (extends BaseSkill)
    ├── student_notification.py  # "Notify student about last week's performance"
    ├── case_escalation.py       # "Escalate this case to the expert"
    └── knowledge_gap_flag.py    # "Flag a knowledge gap for expert review"
```

### The Skill Composition Pattern

```python
class BaseSkill(ABC):
    """Raw capability. No expert context. No persona."""
    @abstractmethod
    def execute(self, params: dict) -> SkillResult: ...
    
    @abstractmethod  
    def get_skill_id(self) -> str: ...

class FunctionalSkill(BaseSkill):
    """Expert-contextualized execution. Always wraps a BaseSkill."""
    def __init__(self, base_skill: BaseSkill, manifest: PersonaManifest, context: dict):
        self.base_skill = base_skill
        self.manifest = manifest   # Injects expert tone, heuristics, drop zones
        self.context = context     # Injects retrieved Master Cases
    
    def execute(self, params: dict) -> SkillResult:
        # 1. Apply persona framing to params
        # 2. Check drop_zone_triggers (refuse if out of scope)
        # 3. Delegate to base_skill.execute()
        # 4. Post-process output through persona communication style
        ...
```

### Tasks: Phase 4

#### 4.1 — Base Skills

- [ ] Define `BaseSkill` abstract class in `skills/base/base_skill.py`
- [ ] Implement `EmailSkill` — wraps an email sending API (or mocked for now)
- [ ] Implement `MessageSkill` — wraps a messaging/notification API
- [ ] Implement `SearchKBSkill` — wraps the Knowledge Hub's `/api/query` endpoint
- [ ] Implement `DraftSkill` — generates a structured text output (email, report, etc.)
- [ ] Unit tests for all base skills

#### 4.2 — Functional Skills

- [ ] Define `FunctionalSkill` abstract class (takes `BaseSkill` + `PersonaManifest` + context)
- [ ] Implement `StudentNotificationSkill` (example: "email student about last week's performance")
  - Uses `EmailSkill` as base
  - Injects expert's tone from `communication_style`
  - Grounds content in retrieved Master Cases
- [ ] Implement `CaseEscalationSkill` (example: "escalate this query to the real expert")
  - Uses `MessageSkill` as base
  - Triggered when confidence < threshold (fallback path)
- [ ] Unit tests for all functional skills

#### 4.3 — Skill Registry

- [ ] Build `SkillRegistry` — maps skill IDs to classes
- [ ] Make it injectable at startup (like the `DomainAdapter`)
- [ ] **Milestone:** `StudentNotificationSkill` executes end-to-end with a real `PersonaManifest` ✅

---

## Phase 5 — Runtime Retrieval & Full Digital Twin Chat

> **Goal:** Build the complete query-time pipeline: user asks → RAG retrieval → confidence scoring → persona routing → expert response

### The Retrieval Pipeline Design

```
POST /chat/message  { expert_id, message, session_id }
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│  1. Load PersonaManifest                                │
│     → Read from Supabase (approved manifest for expert) │
│     → Deserialize PersonaManifest JSON                  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  2. Emergency Bypass Check (pre-RAG)                    │
│     → Keyword/pattern match on message                  │
│     → If triggered → skip all logic → priority queue   │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  3. Embed User Query                                    │
│     → EmbeddingService.embed(message)                   │
│     → Returns 1536-dim vector                           │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  4. RAG Retrieval                                       │
│     → KnowledgeVaultService.search(vector, expert_id)  │
│     → Returns top-k MasterCases with cosine scores     │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  5. Confidence Scoring                                  │
│     → confidence = max(cosine_scores[:k])              │
│     → Compare to manifest.confidence_threshold          │
└──────────────┬─────────────────────┬───────────────────┘
               │                     │
        ≥ threshold             < threshold
               │                     │
┌──────────────▼──────┐   ┌──────────▼──────────────────┐
│  PRIMARY PERSONA    │   │  FALLBACK PERSONA            │
│                     │   │                              │
│  3-Layer Assembly:  │   │  Fallback Identity from      │
│  [Domain Rules]     │   │  DomainAdapter.              │
│  + [Manifest JSON]  │   │  get_fallback_identity()     │
│  + [Top-k Cases]    │   │                              │
│       │             │   │  + Optional: Skill trigger   │
│       ▼             │   │  (CaseEscalationSkill)        │
│  LLM Response       │   │       │                      │
└──────────────┬──────┘   └───────┬──────────────────────┘
               │                  │
               └────────┬─────────┘
                        ▼
                  Response to User
                  (with source citations)
```

### Tasks: Phase 5

#### 5.1 — PersonaManifest Storage & Retrieval

- [ ] Create Supabase table `persona_manifests`:
  ```sql
  CREATE TABLE persona_manifests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    expert_id UUID NOT NULL,
    manifest_version INT NOT NULL,
    manifest_json JSONB NOT NULL,
    shadow_approved BOOLEAN DEFAULT FALSE,
    approved_at TIMESTAMPTZ,
    approved_by TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
  );
  ```
- [ ] Update `CompilerNode` to write to this table after compilation
- [ ] Update `shadow/approve` endpoint to set `shadow_approved=TRUE`
- [ ] Write `ManifestLoader` service — loads approved manifest for a given `expert_id`

#### 5.2 — Chat Endpoint

- [ ] Create `runtime/api/chat.py`:
  ```python
  POST /chat/message
  Body: { expert_id: UUID, message: str, session_id: str }
  Response: { response: str, confidence: float, persona_mode: "primary|fallback", sources: [] }
  ```
- [ ] Implement the full retrieval pipeline (steps 1-5 above) in `runtime/services/retrieval_service.py`
- [ ] Wire `EmbeddingService` + `KnowledgeVaultService` (already built) into retrieval
- [ ] Implement 3-Layer Prompt Assembly in `runtime/services/prompt_assembler.py`
- [ ] Implement LLM call + response formatting
- [ ] Register router in `runtime/main.py`

#### 5.3 — Session Persistence

- [ ] LangGraph Postgres checkpointer is already wired — extend it to the chat flow
- [ ] Each `session_id` maintains conversation history
- [ ] History is included in the context window for multi-turn conversations

#### 5.4 — Source Citations

- [ ] Every response includes `sources: [{ chunk_id, source_doc, section_path }]`
- [ ] This makes the Twin a "Glass Box" — every answer is traceable

#### 5.5 — Integration Tests

- [ ] `tests/test_chat_endpoint.py`:
  - High-confidence query → assert `persona_mode == "primary"`
  - Out-of-scope query → assert `persona_mode == "fallback"`
  - Emergency keyword → assert bypass triggered
- [ ] **Milestone:** Full end-to-end: user asks question → Twin responds in expert's voice ✅

---

## Full Project State Matrix

```
Knowledge Hub
├── [✅] Document ingestion (Hierarchical Parser)
├── [✅] Universal structure builder (gap-preserving)
├── [✅] Embeddings generation
├── [✅] Supabase storage
├── [✅] Divergence scanner (implicit knowledge)
├── [✅] SLM auditor
├── [✅] Scenario generator
├── [✅] HITL breakpoint (Socratic node)
├── [✅] Master Case generation
├── [✅] Query endpoint
├── [⚠️] Automation loop (trigger mechanism)
├── [⚠️] Supabase migrations (partial)
└── [🔲] Frontend Social Learner UI

Expert Persona
├── [✅] PersonaManifest schema
├── [✅] Ingestion Node
├── [✅] AI Journalist Node
├── [✅] Answer Processor Node
├── [✅] Compiler Node
├── [✅] Shadow Mode
├── [✅] 3 Domain Adapters (Healthcare, Recruiting, TechConsulting)
├── [✅] 4 Document Readers (Filesystem, API, SQL, Supabase)
├── [✅] Knowledge Vault + Embedding Services
├── [🔲] KB ↔ Persona Connection (Phase 3)
└── [🔲] PersonaManifest DB storage

Skills Layer
├── [🔲] Base Skills (Email, Message, Search, Draft)
└── [🔲] Functional Skills (Student Notification, Case Escalation)

Runtime Retrieval
├── [🔲] /chat/message endpoint
├── [🔲] Full retrieval pipeline
├── [🔲] 3-Layer Prompt Assembly
├── [🔲] Hat-switching (Primary/Fallback routing)
├── [🔲] Session persistence (multi-turn)
└── [🔲] Source citations
```

---

## Recommended Build Order

```
Week 1: Phase 3 — Connect KB ↔ Persona
         (Highest priority — unblocks everything else)
         Tasks: 3.1 → 3.2 → 3.3 → 3.4
         
Week 2: Phase 4A — Base Skills
         Tasks: 4.1 (all base skills + registry)
         
Week 2: Phase 5A — PersonaManifest storage + Chat endpoint skeleton
         Tasks: 5.1 → 5.2 (first iteration, no fallback yet)
         
Week 3: Phase 4B — Functional Skills + Skill injection into chat
         Tasks: 4.2 → 4.3
         
Week 3: Phase 5B — Confidence scoring + Hat-switching
         Tasks: rest of 5.2 → 5.3 → 5.4 → 5.5
         
Week 4: Integration hardening
         End-to-end tests, session persistence, source citations
```

---

## Open Questions (Decisions Needed Before Starting)

> [!IMPORTANT]
> **Q1: Shared Supabase instance or separate?**
> Are the Knowledge Hub and Expert Persona pointing at the **same** Supabase project? If yes, Phase 3 is straightforward. If not, you'll need to export/import or add a cross-project API layer.

> [!IMPORTANT]
> **Q2: Skills scope for MVP**
> Which functional skills do you want for the first working demo? Suggested MVP set: `StudentNotificationSkill` + `CaseEscalationSkill`. Confirm so we don't over-build.

> [!IMPORTANT]
> **Q3: Frontend**
> The Knowledge Hub's Social Learner UI (React frontend) is not started. Do you want to build it as part of this phase, or defer and test via API/Postman first?

> [!IMPORTANT]
> **Q4: Which expert first?**
> For Phase 3 integration testing, we need a real `expert_id` with documents in the Knowledge Hub. Which expert profile should we use for the first end-to-end run?
