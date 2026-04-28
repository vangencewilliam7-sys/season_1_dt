-- =============================================================================
-- 01_init_schema.sql
-- Digital Twin — Initial Database Schema
-- =============================================================================
-- Run this FIRST in Supabase SQL Editor.
-- Creates: document_chunks, master_cases, pipeline_state, expert_dna
-- Also creates: pgvector extension, HNSW indexes, match_chunks RPC, match_expert_dna RPC
--
-- Safe to re-run — all statements use IF NOT EXISTS guards.
-- =============================================================================


-- Enable the pgvector extension for vector similarity search
create extension if not exists vector;


-- ─────────────────────────────────────────────────────────────────────────────
-- Table: document_chunks
-- Raw ingested knowledge from uploaded PDFs / DOCX files.
-- Stores hierarchical chunks preserving H1 → H2 → H3 structure.
-- Unverified raw content — never used directly for production answers.
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists document_chunks (
    id          uuid    primary key default gen_random_uuid(),
    document_id uuid    not null,
    content     text    not null,
    parent_id   uuid    references document_chunks(id),
    level       int     default 0,
    source_path text,
    embedding   vector(1536),
    metadata    jsonb   default '{}'::jsonb,
    created_at  timestamp with time zone default now()
);


-- ─────────────────────────────────────────────────────────────────────────────
-- Table: master_cases
-- Structured expert decisions extracted via the HITL (Socratic) pipeline.
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists master_cases (
    id               uuid    primary key default gen_random_uuid(),
    expert_decision  text    not null,
    chain_of_thought jsonb   not null,
    logic_tags       text[],
    confidence_note  text,
    impact_archetype text    check (impact_archetype in ('Safety', 'Structural', 'Informational')),
    source_chunk_id  uuid    references document_chunks(id),
    scenario_id      text    not null,
    case_embedding   vector(1536),
    created_at       timestamp with time zone default now(),
    audit_log        jsonb   default '[]'::jsonb
);


-- ─────────────────────────────────────────────────────────────────────────────
-- Table: pipeline_state
-- LangGraph checkpoint persistence.
-- Stores frozen graph state so experts can respond to scenarios asynchronously.
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists pipeline_state (
    document_id uuid    primary key,
    state       jsonb   not null,
    status      text    default 'in_progress',
    updated_at  timestamp with time zone default now()
);


-- ─────────────────────────────────────────────────────────────────────────────
-- Table: expert_dna
-- High-purity Logic Vault — human-verified decisions only.
-- Only records committed by the expert via POST /api/commit land here.
-- This is the ONLY table used for production query answers.
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists expert_dna (
    id               uuid    primary key default gen_random_uuid(),
    scenario_id      text    not null,
    expert_decision  text    not null,
    impact_archetype text    check (impact_archetype in ('Safety', 'Structural', 'Informational')),
    industry         text    default 'fertility',
    reasoning        text,
    embedding        vector(1536),
    created_at       timestamp with time zone default now()
);


-- ─────────────────────────────────────────────────────────────────────────────
-- Indexes: HNSW for fast cosine similarity search
-- ─────────────────────────────────────────────────────────────────────────────
create index if not exists idx_chunks_embedding
    on document_chunks using hnsw (embedding vector_cosine_ops);

create index if not exists idx_cases_embedding
    on master_cases using hnsw (case_embedding vector_cosine_ops);

create index if not exists idx_dna_embedding
    on expert_dna using hnsw (embedding vector_cosine_ops);


-- ─────────────────────────────────────────────────────────────────────────────
-- RPC: match_chunks
-- Cosine similarity search over raw document_chunks.
-- Called by: services/supabase_client.py → semantic_search()
-- ─────────────────────────────────────────────────────────────────────────────
create or replace function match_chunks(
    query_embedding vector(1536),
    match_threshold float,
    match_count     int
)
returns table (
    id          uuid,
    content     text,
    source_path text,
    metadata    jsonb,
    similarity  float
)
language sql stable as $$
    select
        id,
        content,
        source_path,
        metadata,
        1 - (embedding <=> query_embedding) as similarity
    from document_chunks
    where 1 - (embedding <=> query_embedding) > match_threshold
    order by similarity desc
    limit match_count;
$$;


-- ─────────────────────────────────────────────────────────────────────────────
-- RPC: match_expert_dna
-- Cosine similarity search over the high-purity Expert DNA Vault.
-- Called by: services/supabase_client.py → expert_vault_search()
--            app/tools.py → retrieve_expert_knowledge()
-- ─────────────────────────────────────────────────────────────────────────────
create or replace function match_expert_dna(
    query_embedding vector(1536),
    match_threshold float,
    match_count     int
)
returns table (
    id               uuid,
    scenario_id      text,
    expert_decision  text,
    impact_archetype text,
    industry         text,
    reasoning        text,
    similarity       float
)
language sql stable as $$
    select
        id,
        scenario_id,
        expert_decision,
        impact_archetype,
        industry,
        reasoning,
        1 - (embedding <=> query_embedding) as similarity
    from expert_dna
    where 1 - (embedding <=> query_embedding) > match_threshold
    order by similarity desc
    limit match_count;
$$;
