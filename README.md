# Digital Twin — Season 1

**Doctor Digital Twin** — A high-fidelity AI clone of a Fertility Specialist, grounded in verified clinical decisions.

## Structure

```
season_1_dt/
│
├── docs/                    ◄ All documentation (start here)
│
├── backend/                 ◄ Unified FastAPI backend
│   ├── .env                 ◄ Shared credentials (never commit)
│   ├── requirements.txt
│   ├── config/              ◄ Pydantic settings (single source of truth)
│   ├── shared/
│   │   ├── interfaces/      ◄ SOLID abstractions (BaseDocumentReader, BaseLLMProvider, etc.)
│   │   └── schemas/         ◄ PersonaManifest, DocumentChunk, MasterCase
│   ├── knowledge_hub/       ◄ KB pipeline (migrated from knnowledge_Hub/)
│   ├── expert_persona/      ◄ Persona framework (migrated from Expert-Persona-/)
│   │   └── adapters/
│   │       └── healthcare/  ◄ Doctor / HIPAA adapter
│   ├── skills/
│   │   ├── base/            ◄ DraftSkill, NotifySkill, SearchKBSkill
│   │   ├── functional/      ◄ Doctor-specific functional skills
│   │   └── registry.py      ◄ Central skill registry
│   ├── retrieval/           ◄ Runtime retrieval pipeline (Phase 5)
│   └── providers/           ◄ LLM provider implementations
│
├── frontend/                ◄ Next.js UI
│   └── src/
│       ├── app/             ◄ Pages: Dashboard, Chat, KB, Persona, Skills
│       ├── components/      ◄ Layout, shared components
│       └── styles/
│
├── knnowledge_Hub/          ◄ Original KB project (source of truth until migration completes)
└── Expert-Persona-/         ◄ Original Persona project (source of truth until migration completes)
```

## Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn knowledge_hub.api.main:app --reload --port 8001   # KB
uvicorn expert_persona.runtime.main:app --reload --port 8000  # Persona

# Frontend
cd frontend
npm install
npm run dev   # http://localhost:3000
```

## Key Design Principles (SOLID)

| Principle | Where Applied |
|---|---|
| **S**ingle Responsibility | Each module has exactly one job (KB=knowledge, Persona=extraction, Skills=actions) |
| **O**pen/Closed | New domain = new adapter file. New skill = new class. Core never changes. |
| **L**iskov Substitution | `SupabaseReader` drops in anywhere `BaseDocumentReader` is expected |
| **I**nterface Segregation | Separate interfaces: LLMProvider, DocumentReader, DomainAdapter, Skill |
| **D**ependency Inversion | All modules depend on abstractions in `shared/interfaces/`, never concretions |

## Phase Status

| Phase | What | Status |
|---|---|---|
| Phase 1+2 | Expert Persona core + 3 adapters | ✅ Done |
| Phase 3 | KB ↔ Persona bridge (SupabaseReader) | 🔄 Next |
| Phase 4 | Skills Layer (Doctor) | 🏗 Scaffolded |
| Phase 5 | Runtime Retrieval + Chat | 📋 Planned |
