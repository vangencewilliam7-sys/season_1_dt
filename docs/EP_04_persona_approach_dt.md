# Approach: Building the Universal Persona Extraction Framework
> Architect-level execution plan  
> Based on: Business Overview, HLA, LLA, Technical Implementation Plan

---

## 0. Governing Principles

Before writing a single line of code, these constraints must be held non-negotiable:

1. **Layer 1 must never import domain-specific code.** It is the universal core — importing healthcare or HR logic into it breaks the entire multi-vertical promise.
2. **The Persona Manifest is the contract between all layers.** Its JSON schema is locked before Phase 2 begins.
3. **The confidence threshold is a tunable hyperparameter, not a hardcoded value.** It ships as a config variable from day one.
4. **Shadow Mode is not a nice-to-have.** It is the only way to safely deploy. No expert twin goes live without passing Shadow Mode evaluation.

---

## 1. Technology Decisions

| Decision | Choice | Rationale |
|---|---|---|
| **Backend** | Python 3.11 + FastAPI | Async-native, LangChain/LangGraph ecosystem, OpenAPI docs free |
| **LLM Runtime** | Groq API (Llama 3.1 hosted) | Eliminates GPU infra in Phases 1-3; switch to self-hosted (vLLM) post-Phase 4 if cost demands |
| **Orchestration** | LangGraph | Purpose-built for stateful, multi-node agent graphs; native checkpointing |
| **Vector DB** | PostgreSQL 15 + pgvector | Sufficient for MVP; single-service simplicity; migration path to Weaviate documented for Phase 5+ |
| **Embeddings** | `nomic-embed-text` (via Ollama locally / Groq in prod) | Open-weight, high quality, no per-token cost |
| **Session Persistence** | LangGraph Postgres checkpointer | Native to the stack, no additional service |
| **Config Management** | `.env` + Pydantic `BaseSettings` | Type-safe config, easy per-domain override |
| **Testing** | pytest + LangSmith tracing | Unit tests on nodes; LangSmith for end-to-end trace evaluation |

---

## 2. Repository Structure

```
expert-persona/
├── core/                        # Layer 1 — Universal Core (NEVER imports from adapters/)
│   ├── nodes/
│   │   ├── passive_ingestion.py     # Llama 3.1 8B/11B — artifact reader, hypothesis extractor
│   │   ├── ai_journalist.py         # Llama 3.1 3B — conversational extraction loop
│   │   └── manifest_compiler.py     # JSON Manifest builder + validator (Pydantic)
│   ├── graph.py                     # LangGraph state machine definition
│   ├── router.py                    # Confidence evaluator + hat-switching logic
│   └── schemas.py                   # PersonaManifest, BehavioralHypothesis typed schemas
│
├── adapters/                    # Layer 2 — Domain Middleware
│   ├── base_adapter.py              # Abstract base: get_system_prompt(), get_fallback_identity()
│   ├── healthcare_adapter.py        # HIPAA rules, Duty Nurse fallback
│   └── hr_adapter.py                # ATS rules, HR Coordinator fallback
│
├── app/                         # Layer 3 — Data Integration & API
│   ├── db/
│   │   ├── models.py                # SQLAlchemy models: Expert, MasterCase, Session
│   │   └── vector_store.py          # pgvector embedding pipeline + cosine search
│   ├── rag/
│   │   └── retriever.py             # Master Cases RAG pipeline
│   ├── api/
│   │   ├── chat.py                  # POST /chat/message
│   │   ├── extraction.py            # POST /extract/start, GET /extract/status
│   │   └── shadow.py                # GET /shadow/pending, POST /shadow/approve
│   └── main.py                      # FastAPI app init, router registration
│
├── evals/                       # Shadow Mode + Red Team Evaluation Suite
│   ├── red_team_cases.json          # Out-of-bounds query battery
│   ├── eval_runner.py               # Automated evaluation harness
│   └── reports/                     # Empirical eval output (auto-generated)
│
├── docs/                        # Ingested documents (already populated)
├── config/
│   └── settings.py                  # Pydantic BaseSettings — all tunable parameters
├── tests/
│   ├── test_nodes.py
│   ├── test_router.py
│   └── test_adapters.py
└── docker-compose.yml           # PostgreSQL + app services
```

---

## 3. The Persona Manifest Schema (The Contract)

This JSON schema is the **single source of truth** between all layers. It is defined in `core/schemas.py` as a Pydantic model and locked before Phase 2.

```json
{
  "expert_id": "uuid",
  "extracted_at": "ISO8601 timestamp",
  "identity": {
    "name": "string",
    "role": "string",
    "domain": "string"
  },
  "communication_style": {
    "tone": ["direct", "empathetic", "technical"],
    "verbosity": "concise | detailed",
    "preferred_framing": "string — e.g., 'always leads with risk before opportunity'"
  },
  "heuristics": [
    {
      "trigger": "string — situation description",
      "decision": "string — what the expert typically does",
      "reasoning": "string — the why, extracted conversationally"
    }
  ],
  "drop_zone_triggers": [
    "string — topics the expert explicitly does NOT handle"
  ],
  "confidence_threshold": 0.72
}
```

> **Threshold lives in the Manifest.** Each expert's hat-switching sensitivity is calibrated individually during Shadow Mode (Phase 4).

---

## 4. Phased Build Order

### Phase 1 — Layer 1: The Universal Core
**Target: A working extraction pipeline that produces a valid Persona Manifest**

- [ ] Scaffold repo, Docker Compose, FastAPI skeleton
- [ ] Implement `passive_ingestion.py` — feed a CV/transcript → output `behavioral_hypotheses[]`
- [ ] Implement `ai_journalist.py` — multi-turn conversation that probes hypotheses with scenario questions
- [ ] Implement `manifest_compiler.py` — validates and serializes the Persona Manifest JSON
- [ ] Build LangGraph state machine (`graph.py`) connecting all three nodes
- [ ] Implement `router.py` — reads `confidence_threshold` from Manifest, applies hat-switching
- [ ] Write unit tests for all nodes
- [ ] **Milestone**: Interview a test subject (developer persona), generate a valid Manifest, route 10 test queries correctly

---

### Phase 2 — Layer 2: Domain Adapters
**Target: `domain="healthcare"` and `domain="hr"` produce distinct, valid system prompts**

- [ ] Define `base_adapter.py` abstract interface
- [ ] Implement `healthcare_adapter.py` — HIPAA immutable rules, Duty Nurse fallback identity
- [ ] Implement `hr_adapter.py` — ATS rules, HR Coordinator fallback identity
- [ ] Build dynamic prompt assembly: `Layer2.get_system_prompt() + Manifest JSON`
- [ ] Write adapter unit tests: assert that persona JSON cannot override domain safety rules
- [ ] **Milestone**: Single flag change routes to different safety contexts; all rules tests pass

---

### Phase 3 — Layer 3: RAG Integration & API
**Target: Full end-to-end — question in, expert-grounded answer out**

- [ ] Set up PostgreSQL schema: `experts`, `master_cases`, `embeddings`, `sessions`
- [ ] Implement `vector_store.py` — embed and store Master Cases via pgvector
- [ ] Implement `retriever.py` — cosine similarity search, return top-k cases with scores
- [ ] Wire retriever into LangGraph as pre-routing context injection
- [ ] Build `POST /chat/message` endpoint (full 3-layer prompt assembly on each request)
- [ ] Build `POST /extract/start` and `GET /extract/status` endpoints
- [ ] LangGraph Postgres checkpointer for session persistence
- [ ] **Milestone**: User asks a question, system retrieves a Master Case, applies healthcare rules, responds in expert's tone

---

### Phase 4 — Shadow Mode & Evals (QA Gate)
**Target: Mathematical proof that the system is production-safe**

- [ ] Build Shadow Mode routing — AI draft goes to `shadow/pending` dashboard, not end-user
- [ ] Build `POST /shadow/approve` — expert edit updates Persona Manifest (continuous grooming)
- [ ] Populate `red_team_cases.json` with out-of-bounds queries per domain
- [ ] Run `eval_runner.py` — assert hat-switch fires for 100% of red team cases
- [ ] Measure confidence score distribution across 1000 synthetic queries
- [ ] Generate empirical eval report in `evals/reports/`
- [ ] **Milestone**: Production readiness sign-off; empirical report shows 0 hallucination leakage on red team battery

---

## 5. The 3-Layer Prompt Assembly (Implementation Contract)

Every call to the LLM must follow this exact assembly order. Deviation = safety risk.

```python
def assemble_prompt(adapter, manifest, retrieved_cases, user_query):
    system_prompt = (
        adapter.get_system_prompt()          # Layer 2: IMMUTABLE FIRST
        + "\n\n"
        + f"PERSONA:\n{manifest.json()}"     # Layer 1: Expert identity
        + "\n\n"
        + f"RELEVANT CASES:\n{retrieved_cases}"  # Layer 3: RAG context
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_query}
    ]
```

---

## 6. Hat-Switching Implementation (Core Logic)

```python
def route_query(confidence_score: float, manifest: PersonaManifest) -> str:
    if confidence_score >= manifest.confidence_threshold:
        return "primary_persona"   # Respond AS the expert
    else:
        return "fallback_persona"  # Respond as the Deputy

# In the LangGraph graph:
graph.add_conditional_edges(
    "retriever",
    route_query,
    {
        "primary_persona": "primary_response_node",
        "fallback_persona": "fallback_response_node"
    }
)
```

---

## 7. Risk Mitigation Plan

| Risk | Mitigation |
|---|---|
| **Confidence Threshold Calibration** | Ship as `confidence_threshold` in Persona Manifest (per-expert). Phase 4 Shadow Mode provides empirical data to tune it before go-live. |
| **Persona Manifest Drift** | Shadow Mode approval loop writes back to Manifest. Add a `manifest_version` field + auto-trigger re-extraction if expert hasn't reviewed in 90 days. |
| **LLM Hosting** | Use Groq (managed) through Phase 4. Document self-hosted vLLM migration path; trigger only when monthly Groq cost > self-host TCO. |
| **Multi-tenancy Isolation** | Each expert gets a UUID-namespaced schema in PostgreSQL. LangGraph checkpointers are keyed on `{expert_id}:{session_id}`. Row-level security enforced at DB layer. |
| **pgvector Scaling** | Add `HNSW` index from day one (not IVFFlat). Monitor p99 retrieval latency. Weaviate migration path documented at 10M+ vectors. |
| **Drop Zone Validation** | AI Journalist includes a "boundary stress test" round — it intentionally asks edge-case questions and asks the expert to rate their confidence 1-10. Any rating < 6 becomes a `drop_zone_trigger`. |

---

## 8. Definition of Done (Per Phase)

| Phase | Definition of Done |
|---|---|
| 1 | Persona Manifest generated from a test CV; 10/10 routing test queries pass; unit tests green |
| 2 | Domain flag switch verified by automated tests; healthcare and HR prompts inspected by hand |
| 3 | End-to-end Postman/pytest integration test passes for `/chat/message`; session resume verified |
| 4 | Red team battery: 100% fallback trigger rate; empirical report signed off; Shadow Mode approval loop demonstrated |
