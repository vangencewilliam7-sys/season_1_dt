# Understanding: Universal Persona Extraction Framework
> Synthesized from 4 ingested documents — Business Overview, HLA, LLA, Technical Implementation Plan  
> Author perspective: Senior Architect (20+ years)

---

## 1. What Is This System?

This is a **PaaS (Platform-as-a-Service) Digital Twin engine** — it creates a high-fidelity AI clone of a specific human expert, bounded strictly to *that individual's* knowledge, reasoning style, and explicit limitations. It is **not** a general-purpose AI assistant. The core differentiator is that it deliberately knows *what it doesn't know*.

---

## 2. The Three Problems Being Solved

| Problem | Root Cause | Business Impact |
|---|---|---|
| **Bottleneck of Expertise** | High-value experts (Lead Architects, Senior Doctors) are time-constrained | Revenue stalls, client frustration, decisions delayed |
| **Implicit Knowledge Trap** | Experts operate on "muscle memory" — traditional surveys can't capture *why* decisions are made | Critical heuristics never get institutionalized |
| **Trust & Liability Imperative** | Generic AI hallucinates competence outside its training | Legal exposure, brand destruction, patient safety risks |

These three problems compound each other. A system that scales an expert without capturing their *true* reasoning, and without hard guardrails against overreach, is worse than no system at all.

---

## 3. The Conceptual Innovation: Two Key Mental Models

### 3.1 — The "AI Journalist" Extraction Loop
Rather than asking an expert to fill out forms (which captures *what* they do), the system **conversationally interviews** them — probing via scenarios to surface *why* they make decisions. The output is a **Persona Manifest** (a strict JSON artifact) encoding:
- Tone and communication style
- Decision heuristics and risk thresholds
- Explicit `drop_zone_triggers` — boundaries of the expert's competence

### 3.2 — Dynamic "Hat-Switching"
At runtime, for each user query, the system evaluates a **confidence score** against the retrieved expert knowledge. This is binary routing:

```
IF confidence > threshold  →  respond AS the Expert (Primary Persona)
IF confidence < threshold  →  demote to Deputy/Support persona (Fallback)
```

This is the mechanism that delivers the "99.9% hallucination-free guarantee." The system never bluffs — it degrades gracefully to a defined fallback identity rather than fabricating an answer.

---

## 4. Architecture Dissection: 3-Layer Model

The system uses a **strict 3-layer decoupled architecture**, which is its primary engineering strength. Each layer has a single responsibility.

### Layer 1 — The Universal Core (Domain-Agnostic Engine)
This layer has *zero* knowledge of any industry vertical. It only understands:

| Component | Function |
|---|---|
| **Passive Ingestion Node** (Llama 3.1 8B/11B) | Reads unstructured artifacts (CVs, emails, transcripts). Extracts `behavioral_hypotheses` via semantic pattern recognition |
| **AI Journalist Node** (Llama 3.1 3B) | Conversational loop that stress-tests hypotheses. Outputs the final `Persona Manifest` JSON |
| **LangGraph Orchestrator** | The central state machine. Manages node execution, routing logic, confidence evaluation, and conversation state persistence via checkpointers |
| **JSON Manifest Compiler** | Converts the raw extraction output into a validated, structured Persona Manifest |

**Key insight**: Layer 1 uses two different model sizes intentionally. The larger 8B/11B model handles heavy semantic ingestion. The smaller 3B model handles the real-time conversational journalist loop — keeping latency low.

---

### Layer 2 — The Middleware (Domain Adapter)
This is the **"configuration layer"** that makes the platform multi-tenant and multi-vertical. Switching an expert's domain requires only changing a configuration file, not the core code.

| Component | Function |
|---|---|
| **Domain Prompt Compiler** | Prepends immutable, non-overridable industry rules to every prompt (e.g., HIPAA compliance for healthcare, ATS rules for HR) |
| **Fallback Identity Mapper** | A JSON registry defining exactly *who* the Deputy persona is for this domain (e.g., `{"role": "Duty Nurse", "tone": "empathetic, deferential", "action": "Flag for Lead Doctor"}`) |

**Key insight**: The "immutability" of domain rules here is a critical trust mechanism. The Persona Manifest from Layer 1 can never override the safety rules injected by Layer 2.

---

### Layer 3 — The Top Layer (Data + User Interface)
This layer holds the expert's actual *knowledge corpus* and is the only layer that varies per expert deployment.

| Component | Function |
|---|---|
| **PostgreSQL + pgvector** | Vector database storing embedded "Master Cases" — the expert's documented case history |
| **RAG Pipeline** | Cosine similarity search against master cases for each user query |
| **User-facing API / Chatbot** | The `/chat/message` endpoint and frontend interface |
| **Shadow Mode / Evals Suite** | Testing harness — generates AI drafts that route to an expert review dashboard *before* going live |

---

### The 3-Layer Prompt Assembly (Runtime Critical Path)
At inference time, the final prompt is assembled in milliseconds by concatenating 3 components in strict order:

```
[Layer 2: Domain Safety Rules]
    +
[Layer 1: Persona Manifest JSON]
    +
[Layer 3: Retrieved Master Cases (RAG)]
    =
Final LLM Prompt → Response
```

This assembly order is architecturally significant: domain safety rules always appear first, ensuring they cannot be overridden by persona or case data.

---

## 5. The 4-Phase Delivery Plan (As Documented)

| Phase | Goal | Key Milestone |
|---|---|---|
| **Phase 1** | Build Layer 1 (Universal Core) | System interviews a developer, generates a JSON profile, routes test queries by confidence |
| **Phase 2** | Build Layer 2 (Domain Adapters) | Switching `domain="healthcare"` changes all safety rules and fallback behaviors instantly |
| **Phase 3** | Build Layer 3 (RAG + API) | Full end-to-end: user query → RAG retrieval → persona + rules → response |
| **Phase 4** | Shadow Mode & Evals (QA) | "Red Team" evals mathematically prove Hat-Switching works; production sign-off based on empirical reports |

---

## 6. Identified Strengths (Architectural Read)

1. **True Decoupling** — The 3-layer separation is not cosmetic. It means the core AI engine can be developed, tested, and versioned independently of any domain configuration.
2. **Graceful Degradation by Design** — The Hat-Switching mechanism makes the safety boundary *operational*, not just a policy statement.
3. **Continuous Improvement Loop** — Shadow Mode creates a flywheel: expert edits AI drafts → Persona Manifest is updated → the twin gets smarter over time.
4. **Model Right-Sizing** — Using smaller models for specific nodes (journalist loop) is a sound latency management strategy.

---

## 7. Identified Risks & Open Questions (Architect's Eye)

| Risk | Severity | Notes |
|---|---|---|
| **Confidence Threshold Calibration** | 🔴 High | The entire hat-switching mechanism depends on getting this threshold right. Too high = excessive fallback. Too low = hallucination leakage. How is it calibrated? Is it static or adaptive? |
| **Persona Manifest Drift** | 🟡 Medium | As the real expert evolves, the Manifest becomes stale. The Shadow Mode loop is defined, but the *trigger* and *frequency* for re-extraction are not. |
| **pgvector Scaling** | 🟡 Medium | PostgreSQL + pgvector is appropriate for MVP, but at scale (many experts, large case histories), a dedicated vector DB (Pinecone, Weaviate) should be evaluated. |
| **LLM Hosting Strategy** | 🔴 High | Llama 3.1 models require GPU infrastructure. Self-hosted vs. managed inference (Together AI, Groq) needs a firm decision before Phase 1. |
| **Multi-tenancy Isolation** | 🔴 High | If multiple experts are on the same platform, strict data isolation between their Persona Manifests and Master Cases is non-negotiable. The docs don't address this explicitly. |
| **Drop Zone Edge Cases** | 🟡 Medium | The `drop_zone_triggers` are extracted by the journalist. But who validates them? An expert may unknowingly understate or overstate their competence boundaries. |
