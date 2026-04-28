# System Understanding: Knowledge Hub ↔ Expert Persona — Full Pipeline

> **Author Perspective:** Senior Architect reading the full codebase + verbal brief  
> **Last Updated:** 2026-04-28

---

## 1. What Is This System, Really?

This is a **Digital Twin factory** — not a chatbot, not a search engine. It has one job:

> *Take everything an expert has ever written, said, or thought, and crystallize it into a living AI representation of that expert — that can answer questions, maintain scope, and degrade gracefully when it doesn't know something.*

The key innovation is the **full provenance chain**: every answer the Digital Twin gives must be traceable back to a source document, an expert transcript, or an explicit decision. No hallucination. No bluffing. Graceful demotion when confidence drops.

---

## 2. The Five Acts of the Pipeline

The system is best understood as **five sequential acts**, each feeding the next:

```
ACT 1 ────── Knowledge Hub: Document Ingestion & Structure
ACT 2 ────── Knowledge Hub: Metadata, RAG & Embeddings
ACT 3 ────── Knowledge Hub: Validation, Storage & Master Cases
ACT 4 ────── Expert Persona: Extraction & Manifestation
ACT 5 ────── Runtime: Skill Execution & Retrieval
```

### ACT 1 — Document Ingestion & Universal Structure

**What happens:**
1. Raw documents (PDF, DOCX, transcripts) are uploaded into the Knowledge Hub
2. The **Hierarchical Parser** extracts structural headings: H1 → H2 → H3 → body text
3. A **Universal Structure Builder** normalizes all documents to the same hierarchy — if H2 is missing between an H1 and H3, a _placeholder gap_ is preserved (no silent skipping)
4. Output: `List[DocumentChunk]` — each chunk knows its `parent_id`, `level`, `content`, `source_path`

**Why the structure matters:**
The hierarchy is the skeleton of knowledge. If you flatten it, you lose "this fact belongs under this section." The gap-preserving structure builder is critical — it signals *where* knowledge is missing, not just what's present.

---

### ACT 2 — Metadata, RAG & Embeddings

**What happens:**
1. For each `DocumentChunk`, metadata is generated (type, timestamps, tags, parent path) — this is what enables **follow-up questions** to be contextually grounded
2. The **Embedding Service** vectorizes every chunk (1536-dim via OpenAI `text-embedding-3-small`)
3. Embeddings + chunks are stored in **Supabase with pgvector** — enabling cosine similarity retrieval
4. A **RAG (Retrieval-Augmented Generation) index** is built over this data

**Why the metadata matters for follow-ups:**
Follow-up questions are only possible because each chunk carries its lineage (which H1 → H2 → H3 path it came from). When a user asks "tell me more about that," the system can retrieve sibling chunks and parent context.

---

### ACT 3 — Validation, Storage & Master Cases (The Continuous Loop)

**What happens:**
1. **Final Validation**: A structural audit checks for:
   - **Orphan nodes** (chunks with no parent) → flagged and reported
   - **Tree breaks** (gaps in the hierarchy that break parent-child chains) → reported
   - Any chunk that fails Pydantic validation → fails loudly, never silently
2. Every validated chunk is stored in Supabase with a **unique ID** (UUID-namespaced per expert)
3. The system then **scans all documents** and generates **Master Cases** — these are the expert's structured decisions, not raw text:
   ```
   MasterCase = {
       expert_decision: str,
       chain_of_thought: List[str],
       logic_tags: List[str],
       confidence_note: Optional[str],
       source_chunk_id: str
   }
   ```
4. **Implicit Knowledge Capture**: The **Divergence Scanner** finds soft-rule markers ("typically," "usually," "generally") and generates scenarios that force explicit expert clarification — this is where tacit knowledge becomes data
5. **The loop is continuous and infinite** — new documents re-trigger the pipeline; new expert responses generate new Master Cases; the Knowledge Hub never stops learning

> [!IMPORTANT]
> The **implicit knowledge loop** is the highest-value part of the Knowledge Hub. Generic LLMs can process documents. Only this system can surface *why* an expert makes decisions.

---

### ACT 4 — Expert Persona: Extraction & Manifestation

**What happens:**

#### 4.1 — Knowledge Extraction (with Redundancy Awareness)
1. The Persona framework reads from the Knowledge Hub via `BaseDocumentReader` — pulling both:
   - Raw document chunks (the structured knowledge from ACT 1-3)
   - Master Cases (the expert's crystallized decisions)
2. There is **intentional redundancy** with the Knowledge Hub loop — the Persona framework re-reads data that may have just been updated. This is by design: the Persona should always reflect the most current expert state.

#### 4.2 — Question Generation & Expert Interview
1. From the ingested KB + Master Cases, the **AI Journalist Node** generates targeted questions
2. These questions **map to expert-specific gaps and hypotheses** — not generic interview questions
3. The expert answers these questions (via audio recording → STT → transcript, or typed)
4. **LLM fallback questions** are generated for topics the expert didn't address — the LLM fills in plausible behaviors based on context, which the expert then confirms or corrects
5. Output: `generated_questions[]` + `expert_answers[]`

#### 4.3 — Persona Manifestation (The Three Dimensions)

This is the output of the Journalist loop. The `PersonaManifest` encodes:

| Dimension | What it captures | Example |
|---|---|---|
| **Approach** | How the expert frames and attacks problems | "Always leads with risk before opportunity" |
| **Talking Patterns** | Tone, verbosity, preferred analogies, sentence style | "Direct, data-first, uses clinical terminology without jargon" |
| **Psychology** | Mental models, heuristics, decision triggers, blind spots | "Will not make a recommendation without seeing 3+ data points" |

The final `PersonaManifest` JSON includes:
- `identity`: name, role, domain (never hardcoded — always extracted)
- `communication_style`: tone list, verbosity, preferred framing
- `heuristics`: List of `{trigger, decision, reasoning}` — the WHY behind decisions
- `drop_zone_triggers`: explicit out-of-scope boundaries
- `confidence_threshold`: per-expert hat-switching sensitivity (default 0.70)
- `shadow_approved`: quality gate — must be manually approved before production

---

### ACT 5 — Skills & Retrieval

#### 5.1 — The Two Skills

The Digital Twin has two skill levels, and this distinction is crucial:

| Skill Type | Definition | Example |
|---|---|---|
| **Base Skill** | The raw capability — a general action the Twin can perform | "Send a message" / "Draft an email" |
| **Functional Skill** | The expert-contextualized execution — the same action but grounded in the expert's domain, history, and persona | "Send a follow-up email to a student about their missed assignment from last week, in the expert's tone" |

**Key insight:** Base skills are infrastructure. Functional skills are what make the Twin *feel like the expert*. A base skill says "I can send an email." A functional skill says "I can send *this expert's* email to *this specific person* about *this contextual event* — and it will sound exactly like the expert wrote it."

Skills are **composable** — a functional skill is always built on top of one or more base skills, with the `PersonaManifest` and retrieved context injected at execution time.

#### 5.2 — Retrieval (The Runtime Critical Path)

At query time, the retrieval pipeline operates as:

```
User Query
    │
    ▼
Intent Router → classify query type and risk level
    │
    ▼
RAG Retrieval → cosine similarity over Master Cases (pgvector)
    │
    ▼
Confidence Scorer → score = max cosine similarity of top-k results
    │
    ├─── score ≥ threshold ──► Primary Persona response (AS the expert)
    │
    └─── score < threshold ──► Fallback Persona response (Deputy mode)
                                + optionally escalate to real expert
```

The **3-Layer Prompt Assembly** at retrieval time:
```
[Layer 2: Domain Safety Rules]  ← IMMUTABLE, injected first
        +
[Layer 1: PersonaManifest JSON] ← Expert identity + heuristics
        +
[Layer 3: Retrieved Master Cases] ← Specific cases from RAG
        =
Final LLM Prompt → Response
```

Order is contractually enforced — domain safety rules can never be overridden by persona or case data.

---

## 3. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          KNOWLEDGE HUB                                   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  ACT 1: Document Ingestion & Structure                           │   │
│  │                                                                  │   │
│  │  [PDF/DOCX/Audio] → Hierarchical Parser → Universal Structure    │   │
│  │                              │                                   │   │
│  │               H1 ──► H2 ──► H3 ──► Body                        │   │
│  │              (gap-preserving: missing H2 = placeholder)          │   │
│  │                              │                                   │   │
│  │                    DocumentChunk[]                               │   │
│  └──────────────────────────────┬───────────────────────────────────┘   │
│                                 │                                        │
│  ┌──────────────────────────────▼───────────────────────────────────┐   │
│  │  ACT 2: Metadata, RAG & Embeddings                               │   │
│  │                                                                  │   │
│  │  Chunk Metadata ──► Embedding Service ──► pgvector (Supabase)   │   │
│  │  (parent path,       (1536-dim             RAG Index             │   │
│  │   timestamps,         text-embedding-3-small)                    │   │
│  │   tags, lineage)                                                 │   │
│  └──────────────────────────────┬───────────────────────────────────┘   │
│                                 │                                        │
│  ┌──────────────────────────────▼───────────────────────────────────┐   │
│  │  ACT 3: Validation, Storage & Master Cases (Continuous Loop)     │   │
│  │                                                                  │   │
│  │  Final Validator ──► Orphan/Tree-break detection                │   │
│  │        │                                                         │   │
│  │        ▼                                                         │   │
│  │  Supabase DB ──► UUID-namespaced per expert                     │   │
│  │        │                                                         │   │
│  │        ▼                                                         │   │
│  │  Document Scan ──► Master Case Generation                       │   │
│  │        │           {decision, chain_of_thought, logic_tags}     │   │
│  │        │                                                         │   │
│  │        ▼                                                         │   │
│  │  Divergence Scanner ──► Implicit Knowledge Extraction           │   │
│  │  ("typically" / "usually" → Scenario → Expert Response)         │   │
│  │        │                                                         │   │
│  │        └──────────────────────────► ♻ INFINITE LOOP ♻           │   │
│  └──────────────────────────────┬───────────────────────────────────┘   │
└────────────────────────────────-│───────────────────────────────────────┘
                                  │
                     BaseDocumentReader (the bridge)
                                  │
┌─────────────────────────────────▼───────────────────────────────────────┐
│                         EXPERT PERSONA                                   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  ACT 4A: Extraction (reads KB + Master Cases)                    │   │
│  │                                                                  │   │
│  │  Ingestion Node ──► behavioral_hypotheses[]                     │   │
│  │        │            (semantic patterns from documents)          │   │
│  │        ▼                                                         │   │
│  │  AI Journalist ──► generated_questions[]                        │   │
│  │   (LangGraph)       (hypothesis-testing scenarios)              │   │
│  │        │                                                         │   │
│  │  [PAUSE / HITL] ──► Expert answers questions                    │   │
│  │        │             + LLM fallback for gaps                    │   │
│  │        ▼                                                         │   │
│  │  Answer Processor ──► processed_findings{}                      │   │
│  └──────────────────────────────┬───────────────────────────────────┘   │
│                                 │                                        │
│  ┌──────────────────────────────▼───────────────────────────────────┐   │
│  │  ACT 4B: Persona Manifestation                                   │   │
│  │                                                                  │   │
│  │  Compiler Node ──► PersonaManifest.json                         │   │
│  │                    ├─ identity (name, role, domain)             │   │
│  │                    ├─ communication_style (tone, verbosity)     │   │
│  │                    ├─ heuristics [{trigger, decision, WHY}]     │   │
│  │                    ├─ drop_zone_triggers (out-of-scope list)    │   │
│  │                    └─ confidence_threshold (per-expert)         │   │
│  │                                                                  │   │
│  │  Shadow Mode ──► Expert review & approval gate                  │   │
│  └──────────────────────────────┬───────────────────────────────────┘   │
└─────────────────────────────────│───────────────────────────────────────┘
                                  │
                      PersonaManifest (approved)
                                  │
┌─────────────────────────────────▼───────────────────────────────────────┐
│                    SKILLS & RUNTIME RETRIEVAL                           │
│                                                                          │
│  Skills Layer                                                            │
│  ├─ Base Skills: ["send_email", "draft_message", "search_docs", ...]    │
│  └─ Functional Skills: ["notify_student_performance", "escalate_case"]  │
│              ↑ Composed from Base Skills + Manifest + Context            │
│                                                                          │
│  Retrieval Pipeline (per query)                                          │
│                                                                          │
│  User Query ──► Intent Router ──► RAG (pgvector cosine search)          │
│                                          │                               │
│                                   Confidence Score                       │
│                                    /          \                          │
│                              ≥ threshold   < threshold                   │
│                                  │               │                       │
│                         PRIMARY PERSONA    FALLBACK PERSONA              │
│                         (responds AS       (Deputy mode —               │
│                          the expert)        escalate/defer)             │
│                                  │               │                       │
│                    3-Layer Prompt Assembly        │                      │
│                    [Domain Rules]                 │                      │
│                    + [Manifest JSON]              │                      │
│                    + [Retrieved Cases]            │                      │
│                                  │               │                       │
│                              LLM Response ────────┘                     │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Key Design Decisions & Their Rationale

| Decision | What | Why |
|---|---|---|
| **Gap-preserving structure** | H1→H3 with missing H2 leaves a placeholder | Signals missing knowledge, doesn't hide it |
| **Implicit knowledge loop** | "Usually/typically" triggers scenario generation | Tacit expert knowledge can't be captured by surveys; must be surfaced via context |
| **BaseDocumentReader abstraction** | Persona never talks to DB directly | KB format can change (files → API → SQL) with zero Persona code changes |
| **Continuous loop** | Knowledge Hub runs forever | Expert knowledge evolves; the Twin must evolve with it |
| **Shadow Mode gate** | Manifest must be expert-approved | No hallucinated persona goes live; expert corrects the AI's interpretation of themselves |
| **Confidence threshold per-expert** | Each expert has their own 0.0–1.0 threshold | A conservative doctor needs a higher threshold than a general knowledge expert |
| **3-layer prompt assembly order** | Safety rules first, always | Domain constraints can never be overridden by a clever Manifest or a retrieved case |
| **Base vs Functional skills** | Two-tier skill architecture | Base = infrastructure reusability; Functional = expert contextualization |

---

## 5. Data Flow Summary (End-to-End)

```
Document Upload
      ↓
[KB: Parse → Structure → Embed → Validate → Store]
      ↓
[KB: Scan → Master Cases → Diverge → Implicit Loop ↻]
      ↓
[Bridge: BaseDocumentReader reads KB + Master Cases]
      ↓
[Persona: Ingest → Interview → Answer → Compile → Manifest]
      ↓
[Shadow Mode: Expert reviews and approves Manifest]
      ↓
[Runtime: Query → RAG → Confidence → Persona/Deputy → Response]
```

---

## 6. The Redundancy You Mentioned — And Why It's Correct

You noted there's "some redundancy" between the Knowledge Hub loop and the Persona extraction reading the same data. This is **intentional and correct design**:

- The Knowledge Hub **continuously generates and updates** Master Cases (it never stops)
- The Persona framework reads KB + Master Cases as a **snapshot at extraction time**
- Re-extraction can be triggered whenever the KB has evolved significantly (e.g., after 90 days or N new Master Cases)
- The `manifest_version` field tracks this — each approved re-extraction increments the version
- The redundancy ensures the Persona always reflects current expert state without tight coupling to the KB's internal timing

---

## 7. The Optimal Connection Approach

Given your framework, here is the **optimal approach** for connecting Knowledge Hub to Expert Persona:

### Option A: API Bridge (Recommended for Current State)
The Expert Persona's `SupabaseReader` (already built) reads directly from the same Supabase instance that the Knowledge Hub writes to.

```
Knowledge Hub → writes → Supabase (document_chunks + master_cases tables)
Expert Persona → reads → same Supabase via SupabaseReader
```

**Pros:** No duplication of data, real-time reflection of KB updates, already partially implemented  
**Cons:** Tight DB coupling (mitigated by the BaseDocumentReader abstraction)

### Option B: REST API Bridge
Knowledge Hub exposes a `/export/expert/{id}` endpoint; Expert Persona's `APIReader` calls it.

```
Knowledge Hub API → GET /export/expert/{id} → Expert Persona APIReader
```

**Pros:** Fully decoupled, versionable API contract  
**Cons:** More infra to maintain, adds latency

### Recommended: **Option A** for now (same Supabase), with the `APIReader` as the migration path when scale demands it.
