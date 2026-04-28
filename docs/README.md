# Digital Twin — Docs Index

All documentation lives here. Single source of truth.

| File | Purpose |
|---|---|
| `SYS_01_system_understanding.md` | Full theoretical understanding of the pipeline (5 Acts + architecture diagram) |
| `SYS_02_implementation_plan.md` | Implementation plan + project state matrix + what's left to build |
| `KH_01_implementation_approach.md` | Knowledge Hub original implementation approach (phases 0–5) |
| `EP_01_understanding.md` | Expert Persona original understanding doc |
| `EP_02_approach.md` | Expert Persona original approach doc |
| `EP_03_status.md` | Expert Persona Phase 1 & 2 completion status |
| `EP_04_persona_approach_dt.md` | Persona approach specific to the Digital Twin |

---

## Quick Context

- **Expert:** Fertility Specialist / IVF Doctor
- **Domain Adapter:** `healthcare`
- **Supabase:** Shared instance (same project for both Knowledge Hub and Expert Persona)
- **LLM:** Groq (Llama 3.1 family) — ingestion on 70B, journalist loop on 8B
- **Phase 1+2 of Expert Persona:** ✅ Complete (15 + 24 tests passing)
- **Next milestone:** KB ↔ Persona bridge via `SupabaseReader` (Phase 3)
