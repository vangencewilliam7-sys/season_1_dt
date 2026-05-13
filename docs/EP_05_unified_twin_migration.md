# EP_05: Migration Guide — Single-Domain to Unified Multi-Domain Digital Twin Framework

> **Document Type:** Architecture Migration Record  
> **Status:** Implemented ✅  
> **Date:** 2026-05-13  
> **Author:** System Architect

---

## 1. Overview

This document records the architectural migration of the Digital Twin system from a **single-domain, healthcare-only pipeline** to a **Unified Multi-Domain Framework** capable of powering three distinct AI expert twins from a single shared codebase.

### Before vs. After

| Dimension | Before (Single-Domain) | After (Unified Framework) |
|---|---|---|
| **Domains supported** | Healthcare only (hardcoded) | Healthcare, IT, Education |
| **Roles supported** | Implicit "Doctor" | Doctor, Project Manager, Tutor |
| **Domain selection** | Hardcoded `industry = "fertility"` string | `?domain=healthcare&role=doctor` query param |
| **Expert DNA isolation** | No isolation — all records shared a flat table | Strict UUID FK filter per domain — zero cross-twin bleed |
| **Confidence threshold** | Single hardcoded value (`0.90 / 0.75`) | Per-domain, per-adapter tunable threshold |
| **System prompt** | None / generic | Immutable domain-specific safety rules per twin |
| **Fallback identity** | Hardcoded "human doctor" string | Per-twin: Duty Nurse / Scrum Master / Teaching Assistant |
| **LangGraph pipeline** | Unchanged (no domain context in state) | Unchanged (domain context injected into state as data) |

---

## 2. The Three Twins

### 🩺 Twin 1 — Healthcare / Doctor
- **Purpose:** Clinical decision support for physician-level queries
- **Immutable Rules:** HIPAA compliance, no medication prescription without history, mandatory flagging of critical lab values
- **Fallback:** Duty Nurse
- **Confidence Threshold:** `0.70` (doctors see more nuanced, lower-certainty matches)
- **Domain UUID:** `10000000-0000-0000-0000-000000000001`
- **Role UUID:** `20000000-0000-0000-0000-000000000001`

---

### 💻 Twin 2 — IT / Project Manager
- **Purpose:** Agile project governance, sprint planning, risk escalation
- **Immutable Rules:** RACI-based decision framing, no sprint commitment without capacity check, 24-hour blocker surfacing rule
- **Fallback:** Scrum Master
- **Confidence Threshold:** `0.72`
- **Domain UUID:** `10000000-0000-0000-0000-000000000002`
- **Role UUID:** `20000000-0000-0000-0000-000000000002`

---

### 🎓 Twin 3 — Education / Tutor
- **Purpose:** Personalised learning via Socratic questioning and the Feynman technique
- **Immutable Rules:** Never give direct answers — always guide, diagnose knowledge gap before scaffolding, mandatory mastery check at session close
- **Fallback:** Teaching Assistant
- **Confidence Threshold:** `0.75` (higher bar ensures only well-verified tutor logic is served)
- **Domain UUID:** `10000000-0000-0000-0000-000000000003`
- **Role UUID:** `20000000-0000-0000-0000-000000000003`

---

## 3. What Changed and Why

### 3.1 Database Schema

#### Old Problem
The `expert_dna` table had a plain text column `industry TEXT DEFAULT 'fertility'`. There was no way to enforce which records belonged to which domain. A healthcare query could theoretically surface an IT record.

```sql
-- OLD: Fragile, unindexed, ambiguous text field
INSERT INTO expert_dna (scenario_id, expert_decision, industry, embedding)
VALUES ('...', '...', 'fertility', '[...]');
```

#### What Changed
The `industry` column was **dropped**. In its place, `domain_id` and `role_id` foreign keys were added pointing to the 5-layer hierarchy tables seeded by `04_seed_domains_and_roles.sql`.

```sql
-- NEW: Deterministic UUID FK — enforced by the database
INSERT INTO expert_dna (scenario_id, expert_decision, domain_id, role_id, embedding)
VALUES ('...', '...', '10000000-0000-0000-0000-000000000001',
                       '20000000-0000-0000-0000-000000000001', '[...]');
```

**SQL Files Added/Modified:**

| File | Change |
|---|---|
| `sql_schemas/03_hierarchy_and_skills.sql` | Added 5-layer hierarchy tables, dropped `industry` column, added `domain_id`/`role_id` FKs to `expert_dna` and `master_cases` |
| `sql_schemas/04_seed_domains_and_roles.sql` | **NEW** — Seeds 1 Hub, 3 Domains, 3 Roles, 12 Workflows, 15 Tasks, 14 Skills with deterministic UUIDs |

---

### 3.2 New Adapter Layer

The single biggest architectural addition is the `adapters/` module. Instead of embedding domain logic throughout the codebase (hardcoded strings, if-else chains), domain identity is now encoded in a **clean class hierarchy**.

```
backend/app/adapters/
├── __init__.py
├── base_adapter.py          ← Abstract contract (interface)
├── healthcare_adapter.py    ← Doctor twin rules
├── it_adapter.py            ← Project Manager twin rules
├── education_adapter.py     ← Tutor twin rules
└── domain_router.py         ← Factory: get_adapter("healthcare", "doctor")
```

#### The Adapter Contract (`base_adapter.py`)

Every adapter must implement 6 methods:

| Method | Returns | Purpose |
|---|---|---|
| `get_domain_id()` | `str` (UUID) | FK for database writes/queries |
| `get_role_id()` | `str` (UUID) | FK for database writes/queries |
| `get_domain_name()` | `str` | Human-readable label for API responses |
| `get_role_name()` | `str` | Human-readable label for API responses |
| `get_system_prompt()` | `str` | Immutable LLM safety rules for this twin |
| `get_fallback_identity()` | `str` | Who handles out-of-scope queries |
| `get_confidence_threshold()` | `float` | Per-domain RAG confidence floor |

#### How the Router Works

```python
# domain_router.py — single place, no scattered if-else
_ADAPTER_REGISTRY = {
    "healthcare:doctor":      HealthcareAdapter(),
    "it:project_manager":     ITAdapter(),
    "education:tutor":        EducationAdapter(),
}

adapter = get_adapter("healthcare", "doctor")  # → HealthcareAdapter instance
```

---

### 3.3 API Endpoints Updated

All three primary endpoints now require `domain` and `role` query parameters. This is enforced at the FastAPI layer with enum validation — invalid combinations return a `400 Bad Request` immediately.

#### `POST /api/ingest`

```
# OLD
POST /api/ingest
  Body: file=clinical_protocol.pdf

# NEW
POST /api/ingest?domain=healthcare&role=doctor
  Body: file=clinical_protocol.pdf
  Response includes: { "domain": "Healthcare", "role": "Doctor", ... }
```

#### `POST /api/commit`

```
# OLD — fragile text field, defaulted to 'fertility'
POST /api/commit?scenario_id=...&expert_decision=...&archetype=...&industry=fertility

# NEW — FK references, no text field
POST /api/commit?scenario_id=...&expert_decision=...&archetype=...&domain=healthcare&role=doctor
```

The committed record in `expert_dna` now carries `domain_id` and `role_id` UUID columns instead of the old `industry` text string.

#### `POST /api/query`

```
# OLD — no domain isolation
POST /api/query?prompt=How+do+I+handle+a+late+sprint?

# NEW — domain-scoped, per-domain confidence threshold
POST /api/query?prompt=How+do+I+handle+a+late+sprint?&domain=it&role=project_manager
```

Confidence routing now uses the adapter's threshold:
- **Above `threshold + 0.18`** → `status: autonomous`
- **Above `threshold`** → `status: human_in_the_loop`
- **Below `threshold`** → `status: uncertain` → fallback identity named in response

#### `POST /api/chat/message`

```json
// OLD request body
{ "expert_id": "...", "message": "...", "session_id": "..." }

// NEW request body
{
  "expert_id":  "...",
  "message":    "...",
  "session_id": "...",
  "domain":     "education",
  "role":       "tutor"
}
```

The adapter's `system_prompt` is injected into `ChatState.adapter_context` and is available to all chat pipeline nodes.

---

### 3.4 GraphState / ChatState Updated

Both Pydantic state models were extended with three new fields. The pipeline itself was **not touched** — domain context travels as data, not as code imports.

```python
# models/state.py & models/chat_state.py — new fields
domain_id:       Optional[str]            = None  # FK → domains.id
role_id:         Optional[str]            = None  # FK → roles.id
adapter_context: Optional[Dict[str, Any]] = None  # system_prompt, threshold, fallback
```

---

### 3.5 Services Updated

#### `supabase_client.py` — `expert_vault_search()`

```python
# OLD — no domain filter, all DNA records searched globally
def expert_vault_search(self, embedding, limit=1):
    response = self.client.rpc("match_expert_dna", {...}).execute()
    return response.data

# NEW — domain_id FK filter applied before returning results
def expert_vault_search(self, embedding, domain_id=None, limit=1):
    query = self.client.rpc("match_expert_dna", {...})
    if domain_id:
        query = query.eq("domain_id", domain_id)  # Strict FK filter
    return query.execute().data
```

#### `tools.py` — `retrieve_expert_knowledge()`

```python
# OLD — fragile text match (case-sensitive, typo-prone)
results = [r for r in results if r.get("industry", "").lower() == domain.lower()]

# NEW — deterministic UUID FK, passed directly to the DB query
results = _db.expert_vault_search(query_vector, domain_id=domain_id, limit=3)
```

---

## 4. Data Flow Diagram

```
Request: POST /api/ingest?domain=healthcare&role=doctor
         │
         ▼
    FastAPI validates enum params
         │
         ▼
    domain_router.get_adapter("healthcare", "doctor")
         │
         └─▶ HealthcareAdapter
               ├── domain_id  = "10000000-0000-0000-0000-000000000001"
               ├── role_id    = "20000000-0000-0000-0000-000000000001"
               └── system_prompt = "[HIPAA rules, clinical constraints...]"
         │
         ▼
    GraphState(domain_id=..., role_id=..., adapter_context={...})
         │
         ▼
    Universal LangGraph Pipeline  ← UNCHANGED
         │
         ▼
    POST /api/commit?domain=healthcare&role=doctor
         │
         ▼
    expert_dna row:
      ┌─────────────────────────────────────────┐
      │ domain_id  = 10000000-...-000000000001  │  ← FK to Healthcare
      │ role_id    = 20000000-...-000000000001  │  ← FK to Doctor
      │ embedding  = [0.12, 0.87, ...]          │
      │ (no 'industry' text field anymore)      │
      └─────────────────────────────────────────┘
         │
         ▼
    POST /api/query?domain=education&role=tutor&prompt="..."
         │
         ▼
    expert_vault_search(domain_id="10000000-...-000000000003")
         │
         └─▶ Returns ONLY Education Tutor records
              (Healthcare records never appear — FK enforced at DB level)
```

---

## 5. Key Architectural Principles (Non-Negotiable)

1. **The Universal Core never imports from `adapters/`.** The LangGraph pipeline nodes do not know about domain-specific logic. Domain identity is data, not code.

2. **Domain isolation is enforced at the database layer.** The `domain_id` FK filter in `expert_vault_search` is the primary cross-twin isolation mechanism. It is not possible for a healthcare record to appear in an education query.

3. **The confidence threshold is a per-adapter hyperparameter.** It is not hardcoded in `query.py`. Each adapter owns its own threshold, which can be tuned independently based on Shadow Mode evaluation results.

4. **Deterministic UUIDs in seed data.** The Domain and Role UUIDs are hardcoded in the SQL seed file and in the adapter classes. This means adapters can reference them without a database lookup on every request.

---

## 6. How to Add a New Domain/Twin

Adding a 4th domain (e.g., **Legal / Lawyer**) requires exactly 4 steps:

**Step 1 — Add a seed row** in `04_seed_domains_and_roles.sql`:
```sql
INSERT INTO domains (id, hub_id, name) VALUES ('10000000-0000-0000-0000-000000000004', '00000000-...', 'Legal');
INSERT INTO roles (id, domain_id, name) VALUES ('20000000-0000-0000-0000-000000000004', '10000000-...-000000000004', 'Lawyer');
```

**Step 2 — Create** `adapters/legal_adapter.py` implementing all 7 methods of `BaseDomainAdapter`.

**Step 3 — Register** it in `domain_router.py`:
```python
"legal:lawyer": LegalAdapter(),
```

**Step 4 — Add** `"legal"` to `VALID_DOMAINS` and `"lawyer"` to `VALID_ROLES` in `domain_router.py`.

That's it. The pipeline, services, and API endpoints require **zero changes**.
