-- ─────────────────────────────────────────────────────────────────────────────
-- Migration: Add expert_id to Knowledge Hub tables
--
-- Purpose: Links Knowledge Hub data (document_chunks + expert_dna) to
-- Expert-Persona's expert identity system. This enables the SupabaseReader
-- to query: "Give me all knowledge belonging to expert X."
--
-- NOTE: This migration is additive — no existing data is modified.
-- Existing rows will have NULL expert_id until backfilled.
-- ─────────────────────────────────────────────────────────────────────────────

-- Add expert_id to document_chunks
-- Allows SupabaseReader.load(expert_id) to fetch only relevant chunks
ALTER TABLE document_chunks
    ADD COLUMN IF NOT EXISTS expert_id uuid;

CREATE INDEX IF NOT EXISTS idx_chunks_expert_id
    ON document_chunks(expert_id);

-- Add expert_id to expert_dna
-- Allows filtered retrieval of verified decisions per expert
ALTER TABLE expert_dna
    ADD COLUMN IF NOT EXISTS expert_id uuid;

CREATE INDEX IF NOT EXISTS idx_dna_expert_id
    ON expert_dna(expert_id);

-- Add expert_id to master_cases (for completeness)
ALTER TABLE master_cases
    ADD COLUMN IF NOT EXISTS expert_id uuid;

CREATE INDEX IF NOT EXISTS idx_cases_expert_id
    ON master_cases(expert_id);
