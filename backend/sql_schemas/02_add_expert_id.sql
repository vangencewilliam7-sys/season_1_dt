-- =============================================================================
-- 02_add_expert_id.sql
-- Digital Twin — Add expert_id to Knowledge Hub Tables
-- =============================================================================
-- Run this SECOND, after 01_init_schema.sql.
--
-- Purpose:
--   Links Knowledge Hub data (document_chunks, expert_dna, master_cases) to
--   the Expert Persona identity system. This enables SupabaseReader to query:
--   "Give me all knowledge belonging to expert X."
--
-- Safe to re-run — uses ADD COLUMN IF NOT EXISTS and CREATE INDEX IF NOT EXISTS.
-- =============================================================================


-- ─────────────────────────────────────────────────────────────────────────────
-- document_chunks: lets SupabaseReader.load(expert_id) fetch only relevant chunks
-- ─────────────────────────────────────────────────────────────────────────────
alter table document_chunks
    add column if not exists expert_id uuid;

create index if not exists idx_chunks_expert_id
    on document_chunks(expert_id);


-- ─────────────────────────────────────────────────────────────────────────────
-- expert_dna: allows filtered retrieval of verified decisions per expert
-- ─────────────────────────────────────────────────────────────────────────────
alter table expert_dna
    add column if not exists expert_id uuid;

create index if not exists idx_dna_expert_id
    on expert_dna(expert_id);


-- ─────────────────────────────────────────────────────────────────────────────
-- master_cases: links extracted decisions back to the expert who made them
-- ─────────────────────────────────────────────────────────────────────────────
alter table master_cases
    add column if not exists expert_id uuid;

create index if not exists idx_cases_expert_id
    on master_cases(expert_id);
