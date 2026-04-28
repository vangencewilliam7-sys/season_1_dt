-- Enable the pgvector extension to work with embeddings
create extension if not exists vector;

-- ─────────────────────────────────────────────────────────────────────────────
-- Table: document_chunks  (Saraswati Hub — raw ingested knowledge)
-- Stores hierarchical chunks from uploaded PDFs/DOCX with embeddings.
-- This is unverified raw content — never used directly for production answers.
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists document_chunks (
    id          uuid primary key default gen_random_uuid(),
    document_id uuid not null,
    content     text not null,
    parent_id   uuid references document_chunks(id),
    level       int default 0,
    source_path text,
    embedding   vector(1536),
    metadata    jsonb default '{}'::jsonb,
    created_at  timestamp with time zone default now()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- Table: master_cases  (Ganesha Logic Vault — structured expert decisions)
-- Stores parsed, structured expert logic extracted via the HITL pipeline.
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists master_cases (
    id               uuid primary key default gen_random_uuid(),
    expert_decision  text not null,
    chain_of_thought jsonb not null,
    logic_tags       text[],
    confidence_note  text,
    impact_archetype text check (impact_archetype in ('Safety', 'Structural', 'Informational')),
    source_chunk_id  uuid references document_chunks(id),
    scenario_id      text not null,
    case_embedding   vector(1536),
    created_at       timestamp with time zone default now(),
    audit_log        jsonb default '[]'::jsonb
);

-- ─────────────────────────────────────────────────────────────────────────────
-- Table: pipeline_state  (LangGraph checkpoint persistence)
-- Stores frozen graph state so experts can respond to scenarios asynchronously.
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists pipeline_state (
    document_id uuid primary key,
    state       jsonb not null,
    status      text default 'in_progress',
    updated_at  timestamp with time zone default now()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- Table: expert_dna  (High-Purity Logic Vault — human-verified only)
-- Only records committed by the expert via POST /commit land here.
-- This is the ONLY table used for production query answers.
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists expert_dna (
    id               uuid primary key default gen_random_uuid(),
    scenario_id      text not null,
    expert_decision  text not null,
    impact_archetype text check (impact_archetype in ('Safety', 'Structural', 'Informational')),
    industry         text default 'fertility',
    reasoning        text,
    embedding        vector(1536),
    created_at       timestamp with time zone default now()
);

-- Indexes for HNSW cosine similarity search
create index on document_chunks using hnsw (embedding vector_cosine_ops);
create index on master_cases    using hnsw (case_embedding vector_cosine_ops);
create index on expert_dna      using hnsw (embedding vector_cosine_ops);

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
--            tools.py → retrieve_expert_knowledge()
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
