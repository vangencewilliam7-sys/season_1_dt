-- =============================================================================
-- 09_patient_registry.sql
-- Digital Twin — Patient Registry and Profile Management
-- =============================================================================

CREATE TABLE IF NOT EXISTS patients (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name   TEXT NOT NULL,
    email       TEXT UNIQUE,
    dob         DATE,
    gender      TEXT,
    height_cm   DECIMAL,
    weight_kg   DECIMAL,
    base_bmi    DECIMAL,
    clinical_notes JSONB DEFAULT '[]'::jsonb,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Link existing patient_twin_state to the formal registry
ALTER TABLE patient_twin_state 
ADD COLUMN IF NOT EXISTS patient_record_id UUID REFERENCES patients(id) ON DELETE CASCADE;

-- Indexing for fast lookups
CREATE INDEX IF NOT EXISTS idx_patients_email ON patients(email);
