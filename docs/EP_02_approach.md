# Approach: Universal Persona Extraction Framework
### Abstract, Domain-Agnostic Architecture — v3 (Corrected Scope)
> Author perspective: Senior Architect (20+ years)

---

## 0. Scope — What This Framework Does and Does Not Do

This is a **persona extraction framework**. Its job is exactly one thing:

```
INPUT:   Existing Knowledge Hub + Master Cases (already built, WIP)
PROCESS: Read → Ingest → Interview → Compile
OUTPUT:  PersonaManifest (a structured JSON profile of the expert)
```

**This framework does NOT:**
- Build or store Master Cases
- Run a runtime query-answering chatbot
- Manage a vector database
- Build a RAG pipeline

Those are downstream consumers of the `PersonaManifest` this framework produces.
The framework's responsibility ends when the Manifest is generated and validated.

---

## 1. The Correct Mental Model

```
┌─────────────────────────────────────────────────────────────┐
│           EXISTING (not built by this framework)            │
│                                                             │
│   Knowledge Hub  ──┐                                        │
│                    ├──► Raw Expert Documents                │
│   Master Cases  ───┘                                        │
└────────────────────────────┬────────────────────────────────┘
                             │  read (via BaseDocumentReader)
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              THIS FRAMEWORK  (what we build)                │
│                                                             │
│  Layer 1 ──► Ingest → AI Journalist → Compile               │
│  Layer 2 ──► Domain rules narrow the extraction context     │
│  Layer 3 ──► Connect reader to KB + API + Shadow Mode test  │
│                                                             │
│                        OUTPUT: PersonaManifest.json         │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│        DOWNSTREAM (not built by this framework)             │
│                                                             │
│   Digital Twin Runtime, Hat-Switch Router, Chatbot UI...    │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Governing Principles

1. **Layer 1 has zero domain knowledge.** It reads documents and extracts persona. That's all.
2. **`PersonaManifest` is the only output contract.** It is the single artifact this framework produces.
3. **`BaseDocumentReader` is the only integration point with the existing KB.** The framework never talks directly to any storage system — only through this interface.
4. **`DomainAdapter` is the only plugin point for new verticals.** Implement 4 methods. That's the entire integration cost.
5. **Shadow Mode gates every production Manifest.** The expert must review and approve the extracted Manifest before it is marked production-ready.

---

## 3. Technology Decisions

| Decision | Choice | Rationale |
|---|---|---|
| **Backend** | Python 3.11 + FastAPI | Async-native; LangGraph ecosystem |
| **Orchestration** | LangGraph | Stateful multi-node pipeline; native checkpointing for long extractions |
| **LLM (Ingestion)** | Llama 3.1 8B/70B via Groq | Heavy semantic pass over large documents |
| **LLM (Journalist)** | Llama 3.1 3B via Groq | Low-latency conversational loop; structured JSON output |
| **Config** | Pydantic `BaseSettings` + `.env` | Type-safe; per-deployment override via env vars |
| **Testing** | pytest + LangSmith | Node unit tests + full trace evaluation |
| **Session Persistence** | LangGraph Postgres checkpointer | Extractions can be long; must survive interruptions |

> No vector database. No embedding model. No RAG pipeline. Those are not needed for extraction.

---

## 4. Abstract Repository Structure

```
persona-framework/
│
├── core/                              # ══ LAYER 1: Universal Extraction Engine ══
│   │                                  # Zero domain knowledge. Pure extraction logic.
│   ├── schemas.py                     # PersonaManifest, BehavioralHypothesis — THE CONTRACT
│   ├── graph.py                       # LangGraph state machine (nodes + edges)
│   │
│   ├── nodes/
│   │   ├── ingestion_node.py          # Reads raw documents → behavioral_hypotheses[]
│   │   ├── journalist_node.py         # Conversational loop → draft PersonaManifest
│   │   └── compiler_node.py          # Validates + serializes final Manifest JSON
│   │
│   └── providers/
│       └── base_llm.py               # abstract class BaseLLMProvider (swap Groq/OpenAI/Ollama)
│
├── adapters/                          # ══ LAYER 2: Domain Adapter Plugins ══
│   ├── base_adapter.py               # abstract class DomainAdapter  ← THE PLUGIN CONTRACT
│   ├── _reference_impl/
│   │   └── generic_adapter.py        # Blank-slate adapter for testing Layer 1 in isolation
│   └── <your_domain>/
│       └── <domain>_adapter.py       # Your domain plugin. Only file you write per vertical.
│
├── runtime/                           # ══ LAYER 3: KB Integration + API + Testing ══
│   │
│   ├── readers/
│   │   ├── base_reader.py            # abstract class BaseDocumentReader ← KB INTEGRATION POINT
│   │   ├── filesystem_reader.py      # Concrete: reads from a local folder of files
│   │   └── api_reader.py             # Concrete: reads from an external KB API endpoint
│   │
│   ├── api/
│   │   ├── extraction.py             # POST /extract/start  |  GET /extract/{id}/status
│   │   └── shadow.py                 # GET /shadow/pending  |  POST /shadow/{id}/approve
│   │
│   └── main.py                       # FastAPI app init — adapter + reader injected at startup
│
├── evals/                             # Shadow Mode + Manifest quality evaluation
│   ├── manifest_validator.py         # Structural + semantic validation of output Manifest
│   ├── cases/
│   │   └── extraction_test_cases/   # Sample expert documents for testing extraction quality
│   └── reports/                      # Auto-generated validation reports per expert
│
├── providers/
│   ├── groq_llm.py                   # Concrete BaseLLMProvider → Groq API
│   └── ollama_llm.py                 # Concrete BaseLLMProvider → local Ollama
│
├── tests/
│   ├── test_core_nodes.py            # Layer 1 unit tests (generic adapter, sample docs)
│   ├── test_adapter_contract.py      # Validates any adapter implements the full contract
│   ├── test_reader_contract.py       # Validates any reader implements BaseDocumentReader
│   └── test_end_to_end.py            # Full extraction pipeline: docs in → Manifest out
│
├── config/
│   └── settings.py                   # Pydantic BaseSettings
│
└── docker-compose.yml                # Postgres (for LangGraph checkpointing only) + app
```

---

## 5. The Three Abstract Contracts

### 5.1 — `PersonaManifest` (The Output — Layer 1 output, all layers read it)

Defined in `core/schemas.py`. This is the only artifact this framework produces.

```python
from pydantic import BaseModel, Field
from typing import List
from uuid import UUID
from datetime import datetime

class Heuristic(BaseModel):
    trigger: str       # "When X situation occurs..."
    decision: str      # "...the expert typically does Y..."
    reasoning: str     # "...because of Z"  ← the implicit knowledge

class PersonaManifest(BaseModel):
    expert_id: UUID
    extracted_at: datetime
    manifest_version: int = 1
    source_documents: List[str]        # Which KB docs + master cases were read

    identity: dict                     # name, role, domain — extracted, never hardcoded
    communication_style: dict          # tone, verbosity, preferred framing
    heuristics: List[Heuristic]        # The expert's decision-making patterns
    drop_zone_triggers: List[str]      # Topics the expert does NOT handle
    confidence_threshold: float = 0.70 # For downstream runtime use (hat-switching)

    # Quality gates
    shadow_approved: bool = False
    approved_by: str | None = None
    approved_at: datetime | None = None
```

---

### 5.2 — `DomainAdapter` (Layer 2 Plugin — 4 methods, 1 file per vertical)

```python
from abc import ABC, abstractmethod

class DomainAdapter(ABC):
    """
    Implement this to add any new domain vertical.
    The extraction framework ONLY calls these 4 methods.
    """

    @abstractmethod
    def get_domain_id(self) -> str:
        """Unique slug. e.g. 'healthcare', 'recruiting', 'course_platform'"""

    @abstractmethod
    def get_immutable_rules(self) -> str:
        """
        Non-overridable constraints injected into every extraction prompt.
        E.g. compliance rules, ethical boundaries, scope limits.
        """

    @abstractmethod
    def get_fallback_identity(self) -> dict:
        """
        Who the twin becomes when a query is out of scope.
        Schema: {"role": str, "tone": str, "action": str}
        """

    @abstractmethod
    def get_extraction_context(self) -> str:
        """
        Domain-specific framing for the AI Journalist's system prompt.
        Helps it ask the right scenario questions for this vertical.
        """
```

---

### 5.3 — `BaseDocumentReader` (Layer 3 — The Only Integration Point with Existing KB)

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

@dataclass
class Document:
    source: str        # Where this came from (file path, URL, record ID)
    content: str       # Raw text content
    metadata: dict     # Type, date, tags — whatever the KB provides

class BaseDocumentReader(ABC):
    """
    Abstract interface to the existing Knowledge Hub and Master Cases.
    Implement this to connect the framework to any storage system.
    The framework never calls any DB or API directly — only this interface.
    """

    @abstractmethod
    def load(self, expert_id: str) -> List[Document]:
        """
        Load all available documents for this expert
        from the Knowledge Hub and Master Cases.
        Returns raw Document objects — no embedding, no chunking, no storage.
        """
```

**Two concrete readers — one for each likely source:**

```python
# runtime/readers/filesystem_reader.py
# Reads from a local folder — for development or file-based KBs

# runtime/readers/api_reader.py
# Reads from an HTTP API — for KBs with a query endpoint
# Implement with whatever URL/auth the existing KB exposes
```

---

## 6. Extraction Pipeline (The Core Flow)

This is what happens when an extraction is triggered — entirely within this framework.

```
POST /extract/start  { expert_id, domain, reader_config }
         │
         ▼
┌─────────────────────────────────────────────────────┐
│  LangGraph State Machine                            │
│                                                     │
│  1. BaseDocumentReader.load(expert_id)              │
│     → List[Document] from KB + Master Cases         │
│                                                     │
│  2. IngestionNode                                   │
│     → Reads documents semantically                  │
│     → Extracts behavioral_hypotheses[]              │
│                                                     │
│  3. JournalistNode                                  │
│     → Conversational loop with the expert           │
│     → Tests hypotheses via scenario questions       │
│     → Narrows into confirmed patterns               │
│                                                     │
│  4. CompilerNode                                    │
│     → Validates structure                           │
│     → Serializes PersonaManifest JSON               │
│     → Sets shadow_approved = False                  │
│                                                     │
└─────────────────────────────────────────────────────┘
         │
         ▼
  GET /shadow/pending
  Expert reviews the draft Manifest
  Edits → corrections written back
         │
         ▼
  POST /shadow/{id}/approve
  shadow_approved = True  →  Manifest is production-ready
```

---

## 7. Phased Build Plan

### Phase 1 — Build the Universal Core (Layer 1)
> Goal: A working extraction pipeline that produces a valid PersonaManifest from raw text.

- [ ] Scaffold repo, Docker Compose, FastAPI skeleton, `import-linter` rules
- [ ] Define and freeze `PersonaManifest` Pydantic schema in `core/schemas.py`
- [ ] Define `BaseLLMProvider` abstract interface and `groq_llm.py` concrete implementation
- [ ] Implement `IngestionNode` — reads `List[Document]` → outputs `behavioral_hypotheses[]`
- [ ] Implement `JournalistNode` — multi-turn conversational loop → draft Manifest fields
- [ ] Implement `CompilerNode` — validates and serializes final `PersonaManifest`
- [ ] Wire all three nodes into `graph.py` LangGraph state machine
- [ ] Write `GenericAdapter` (blank-slate) in `adapters/_reference_impl/` for testing
- [ ] Write `FilesystemReader` for testing without a real KB
- [ ] Unit tests: all nodes pass with generic adapter + sample test documents
- [ ] **Milestone**: Feed a folder of sample expert documents → generate a valid, structured `PersonaManifest.json`

---

### Phase 2 — Build the Plugin System (Layer 2)
> Goal: Any new domain = implement 4 methods in 1 file. Prove this with one real reference adapter.

- [ ] Finalize and document `DomainAdapter` abstract interface
- [ ] Write `test_adapter_contract.py` — validates any adapter class is framework-compliant
- [ ] Build **Reference Adapter #1** for the first real vertical (to be confirmed — recruiting, healthcare, or course platform)
- [ ] Verify: adapter rules cannot be softened by Manifest content (adversarial prompt test)
- [ ] Verify: swapping the injected adapter at startup changes extraction context with zero core code changes
- [ ] Document the "Add a New Domain" guide: 4 methods → 1 file → tests pass → done
- [ ] **Milestone**: Two adapters produce demonstrably different extraction contexts and fallback identities from identical raw documents

---

### Phase 3 — Integrate with Existing Knowledge Sources (Layer 3)
> Goal: Connect the framework to the real Knowledge Hub and Master Cases. No storage is built — only the reader interface is implemented.

- [ ] Finalize `BaseDocumentReader` abstract interface
- [ ] Write `test_reader_contract.py` — validates any reader is framework-compliant
- [ ] Implement concrete reader(s) that connect to the existing KB:
  - [ ] `FilesystemReader` — if KB exposes files/exports
  - [ ] `APIReader` — if KB exposes an HTTP query endpoint
  - [ ] (other reader as needed based on actual KB format)
- [ ] Wire reader into LangGraph as the first step of the extraction graph
- [ ] Build `POST /extract/start` API endpoint — accepts `expert_id`, `domain`, reader config
- [ ] Build `GET /extract/{id}/status` — returns extraction progress + current node
- [ ] Build `GET /shadow/pending` — expert review queue
- [ ] Build `POST /shadow/{id}/approve` — marks Manifest as production-ready
- [ ] LangGraph Postgres checkpointer — extractions survive server restarts
- [ ] **Milestone**: Point the framework at the real Knowledge Hub + Master Cases → full `PersonaManifest` generated for a real expert → expert reviews and approves via Shadow Mode

---

### Phase 4 — Shadow Mode & Quality Evaluation Gate
> Goal: Empirically validate the quality of the extracted Manifests before any downstream system relies on them.

- [ ] Build `manifest_validator.py` — structural checks (all required fields present) + semantic checks (heuristics are specific, not generic platitudes)
- [ ] Define quality rubric: minimum heuristics count, drop_zone completeness, tone specificity score
- [ ] Deploy Shadow Mode: every new extraction routes to expert review dashboard before `shadow_approved = True`
- [ ] Expert edits AI draft → corrections written back to Manifest → `manifest_version` incremented
- [ ] Build red team test: deliberately feed documents with known "edge topics" → verify `drop_zone_triggers` capture them
- [ ] Run extraction across 3 different expert profiles → compare Manifest quality across domains
- [ ] Generate empirical quality report in `evals/reports/`
- [ ] **Milestone**: Production sign-off gated on: 3 diverse expert Manifests approved in Shadow Mode; red team edge cases correctly captured in drop zones; quality report generated

---

## 8. How to Add a New Domain (Extension Model)

```
Step 1: Create the file
        adapters/<your_domain>/<your_domain>_adapter.py

Step 2: Implement DomainAdapter (4 methods)
        get_domain_id()           → slug string
        get_immutable_rules()     → non-overridable constraints string
        get_fallback_identity()   → deputy persona dict
        get_extraction_context()  → journalist framing string

Step 3: Run the contract test
        pytest tests/test_adapter_contract.py --adapter=<your_domain>
        → All pass = framework-compliant

Step 4: Set the env var
        DOMAIN_ADAPTER=<your_domain>

Step 5: Run an extraction
        POST /extract/start  { expert_id, domain: "<your_domain>" }
```

Zero changes to Layer 1. Zero changes to the extraction engine. Zero changes to the API.

---

## 9. Risk Mitigation

| Risk | Mitigation |
|---|---|
| **KB Format Unknown** | `BaseDocumentReader` is abstract — any format the KB uses (files, API, DB records) becomes a concrete reader implementation. Framework is insulated from format changes. |
| **Extraction Incompleteness** | `CompilerNode` uses Pydantic validation — a Manifest with missing required fields fails compilation and triggers a re-Journalist loop, not a silent bad output. |
| **Journalist Asks Wrong Questions** | `get_extraction_context()` in the adapter gives the Journalist domain framing. Wrong questions = update this method — zero impact on Layer 1. |
| **Manifest Goes Stale** | `manifest_version` increments on every edit. `extracted_at` + `approved_at` timestamps make drift visible. Re-extraction trigger when `approved_at` > 90 days. |
| **LLM Provider** | Groq through all 4 phases. `BaseLLMProvider` makes it a one-file swap if needed. |
| **Long Extractions** | LangGraph Postgres checkpointer persists state. Extraction can resume from last completed node after interruption. |

---

## 10. Definition of Done (Per Phase)

| Phase | Done When |
|---|---|
| **Phase 1** | Valid `PersonaManifest` generated from sample docs using `GenericAdapter`. All node unit tests pass. Import isolation verified. |
| **Phase 2** | Any adapter passing `test_adapter_contract.py` is compliant. Two adapters produce different extraction contexts from same docs. |
| **Phase 3** | Framework reads from real KB + Master Cases. Full Manifest generated for a real expert. Shadow Mode review loop functional. |
| **Phase 4** | 3 expert Manifests approved in Shadow Mode. Red team edge cases in drop zones. Quality report generated and signed off. |
