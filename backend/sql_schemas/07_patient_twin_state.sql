-- =============================================================================
-- 07_patient_twin_state.sql
-- Digital Twin — Persistent Patient Mirror State
-- =============================================================================
-- Stores real-time patient confidence indexes and dynamic risk triage mutations.
-- =============================================================================

CREATE TABLE IF NOT EXISTS patient_twin_state (
    patient_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id   TEXT NOT NULL,
    mirror_state JSONB NOT NULL DEFAULT '{}'::jsonb,
    updated_at   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_patient_twin_session ON patient_twin_state(session_id);
