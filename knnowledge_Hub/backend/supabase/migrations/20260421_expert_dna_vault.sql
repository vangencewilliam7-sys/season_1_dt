-- Expert DNA Vault: The high-purity repository of verified logic
CREATE TABLE IF NOT EXISTS expert_dna (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scenario_id VARCHAR(255) NOT NULL,
    expert_decision TEXT NOT NULL,
    chain_of_thought JSONB,
    logic_tags TEXT[],
    impact_archetype VARCHAR(50), -- Safety, Structural, Informational
    industry VARCHAR(100),
    source_chunk_id UUID REFERENCES knowledge_chunks(id),
    embedding VECTOR(1536), -- Matches text-embedding-3-small
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Enable vector search on the vault
CREATE INDEX IF NOT EXISTS expert_dna_embedding_idx ON expert_dna 
USING ivfflat (embedding list_cosine_ops)
WITH (lists = 100);
