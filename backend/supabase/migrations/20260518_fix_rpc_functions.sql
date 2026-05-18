-- =============================================================================
-- fix_rpc_functions.sql
-- Fixes two broken RPC functions in Supabase
-- =============================================================================
-- Run this in Supabase SQL Editor.
--
-- Issue 1: match_chunks returns uuid but document_chunks.id is text
-- Issue 2: match_expert_dna has two overloaded versions causing ambiguity
-- =============================================================================


-- ─────────────────────────────────────────────────────────────────────────────
-- FIX 1: match_chunks — change return type of 'id' from uuid to text
-- ─────────────────────────────────────────────────────────────────────────────
-- Root cause: document_chunks.id is stored as TEXT in the actual DB,
-- but the RPC function declared it as UUID in the return type.

DROP FUNCTION IF EXISTS match_chunks(vector(1536), float, int);

CREATE OR REPLACE FUNCTION match_chunks(
    query_embedding vector(1536),
    match_threshold float,
    match_count     int
)
RETURNS TABLE (
    id          text,       -- was uuid, actual column is text
    content     text,
    source_path text,
    metadata    jsonb,
    similarity  float
)
LANGUAGE sql STABLE AS $$
    SELECT
        id,
        content,
        source_path,
        metadata,
        1 - (embedding <=> query_embedding) AS similarity
    FROM document_chunks
    WHERE 1 - (embedding <=> query_embedding) > match_threshold
    ORDER BY similarity DESC
    LIMIT match_count;
$$;


-- ─────────────────────────────────────────────────────────────────────────────
-- FIX 2: match_expert_dna — remove ambiguous overload
-- ─────────────────────────────────────────────────────────────────────────────
-- Root cause: Two versions exist (3-param and 5-param). PostgREST cannot
-- disambiguate when called with 3 params. Solution: drop BOTH, recreate
-- one clean version with DEFAULT NULLs for the optional params.

DROP FUNCTION IF EXISTS match_expert_dna(vector(1536), float, int);
DROP FUNCTION IF EXISTS match_expert_dna(vector(1536), float, int, uuid, uuid);

CREATE OR REPLACE FUNCTION match_expert_dna(
    query_embedding  vector(1536),
    match_threshold  float,
    match_count      int,
    p_domain_id      uuid DEFAULT NULL,
    p_workflow_id    uuid DEFAULT NULL
)
RETURNS TABLE (
    id               uuid,
    scenario_id      text,
    expert_decision  text,
    impact_archetype text,
    similarity       float
)
LANGUAGE sql STABLE AS $$
    SELECT
        id,
        scenario_id,
        expert_decision,
        impact_archetype,
        1 - (embedding <=> query_embedding) AS similarity
    FROM expert_dna
    WHERE 1 - (embedding <=> query_embedding) > match_threshold
      AND (p_domain_id IS NULL OR domain_id = p_domain_id)
      AND (p_workflow_id IS NULL OR workflow_id = p_workflow_id)
    ORDER BY similarity DESC
    LIMIT match_count;
$$;
