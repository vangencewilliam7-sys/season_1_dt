-- =============================================================================
-- 08_seed_obesity_test_scenarios.sql
-- Digital Twin Platform — Seed Data for Obesity Workflow & Test Scenarios
-- =============================================================================
-- This script seeds the specific workflows, tasks, skills, and Expert DNA for 
-- the Obesity and Metabolic Diagnosis workflow, along with 4 patient scenarios 
-- for the patient_twin_state.
-- 
-- Note: UUIDs have been standardized and schema columns mapped to match the 
-- existing 01_init_schema, 03_hierarchy, and 07_patient schemas.
-- =============================================================================

-- We use the existing Hub ID
-- Hub ID: 00000000-0000-0000-0000-000000000001

-- ==========================================
-- BASE SCHEMA INITIALIZATION (Self-Contained)
-- ==========================================

CREATE TABLE IF NOT EXISTS hubs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT NOT NULL,
    description TEXT,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS domains (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hub_id      UUID NOT NULL REFERENCES hubs(id) ON DELETE CASCADE,
    name        TEXT NOT NULL,
    description TEXT,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS roles (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain_id   UUID NOT NULL REFERENCES domains(id) ON DELETE CASCADE,
    name        TEXT NOT NULL,
    description TEXT,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS workflows (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id     UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    name        TEXT NOT NULL,
    description TEXT,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tasks (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    name        TEXT NOT NULL,
    description TEXT,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS skill_definitions (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_name              TEXT NOT NULL UNIQUE,
    skill_type              TEXT NOT NULL,
    is_active               BOOLEAN DEFAULT true,
    requires_human_approval BOOLEAN DEFAULT false,
    created_at              TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS workflow_skills (
    workflow_id                    UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    skill_id                       UUID NOT NULL REFERENCES skill_definitions(id) ON DELETE CASCADE,
    functional_context_description TEXT,
    PRIMARY KEY (workflow_id, skill_id)
);

CREATE TABLE IF NOT EXISTS expert_dna (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id      TEXT NOT NULL,
    expert_decision  TEXT NOT NULL,
    chain_of_thought JSONB,
    impact_archetype TEXT,
    domain_id        UUID REFERENCES domains(id) ON DELETE SET NULL,
    role_id          UUID REFERENCES roles(id) ON DELETE SET NULL,
    workflow_id      UUID REFERENCES workflows(id) ON DELETE SET NULL,
    task_id          UUID REFERENCES tasks(id) ON DELETE SET NULL,
    embedding        vector(1536),
    created_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- LAYER 1: HUB SEEDING
-- ==========================================
INSERT INTO hubs (id, name, description)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'Digital Twin Platform',
    'The unified root hub for all domain-specific AI expert twins.'
) ON CONFLICT (id) DO NOTHING;

-- ==========================================
-- LAYER 2 & 3: DOMAIN AND ROLE SEEDING
-- ==========================================
-- Domain: Healthcare (Using existing ID 1000...)
INSERT INTO domains (id, hub_id, name, description) 
VALUES (
    '10000000-0000-0000-0000-000000000001', 
    '00000000-0000-0000-0000-000000000001',
    'Healthcare', 
    'Clinical domain covering patient diagnostics, metabolic health, and triage workflows.'
) ON CONFLICT (id) DO UPDATE SET description = EXCLUDED.description;

-- Role: Doctor (Using existing ID 2000...)
-- Note: system_persona_prompt is handled by the application Adapter, so we store it in description.
INSERT INTO roles (id, domain_id, name, description) 
VALUES (
    '20000000-0000-0000-0000-000000000001', 
    '10000000-0000-0000-0000-000000000001', 
    'Doctor', 
    'Senior Metabolic and Obesity Specialist with 20+ years of clinical experience. Analyzes anthropometrics, labs, and symptomatic proxies.'
) ON CONFLICT (id) DO UPDATE SET description = EXCLUDED.description;


-- ==========================================
-- LAYER 4 & 5: WORKFLOWS AND TASKS
-- ==========================================
INSERT INTO workflows (id, role_id, name, description)
VALUES (
    '30000000-0000-0000-0000-000000000100', 
    '20000000-0000-0000-0000-000000000001', 
    'Obesity & Metabolic Diagnosis', 
    'Clinical evaluation of BMI, metabolic vitals, lifestyle risk factors, and EOSS staging.'
) ON CONFLICT (id) DO NOTHING;

-- Note: task_order and structural_rules are merged into description to match schema.
INSERT INTO tasks (id, workflow_id, name, description)
VALUES 
(
    '40000000-0000-0000-0000-000000000101', 
    '30000000-0000-0000-0000-000000000100', 
    'Calculate BMI & Screen Vitals', 
    'Order: 1. Rules: require height, weight; allow_proxy true.'
),
(
    '40000000-0000-0000-0000-000000000102', 
    '30000000-0000-0000-0000-000000000100', 
    'Evaluate Comorbidities', 
    'Order: 2. Rules: require hba1c, lipids, bp; allow_proxy true.'
),
(
    '40000000-0000-0000-0000-000000000103', 
    '30000000-0000-0000-0000-000000000100', 
    'Formulate Intervention Plan', 
    'Order: 3. Rules: require eoss_stage.'
) ON CONFLICT (id) DO NOTHING;


-- ==========================================
-- WORKFLOW SKILLS MAPPING
-- ==========================================
-- Note: parameter_schema is managed by code (pydantic), so we insert basic skill info.
INSERT INTO skill_definitions (id, skill_name, skill_type, is_active, requires_human_approval)
VALUES (
    '50000000-0000-0000-0000-000000000100', 
    'Human Escalation Trigger (Obesity)', 
    'Functional',
    true,
    true
) ON CONFLICT (id) DO NOTHING;

INSERT INTO workflow_skills (workflow_id, skill_id, functional_context_description)
VALUES (
    '30000000-0000-0000-0000-000000000100', 
    '50000000-0000-0000-0000-000000000100', 
    'If secondary obesity causes are suspected (e.g., severe hypothyroidism, Cushing''s) or acute symptoms like chest pain or severe shortness of breath arise, escalate immediately to an endocrinologist or emergency care.'
) ON CONFLICT (workflow_id, skill_id) DO NOTHING;


-- ==========================================
-- HIGH-PURITY VAULT (EXPERT DNA)
-- ==========================================
-- Note: embeddings are set to NULL because pgvector expects 1536 dimensions. 
-- The backend embedder service handles the vectorization of these rules.
INSERT INTO expert_dna (id, role_id, workflow_id, scenario_id, expert_decision, chain_of_thought, impact_archetype)
VALUES 
(
    '60000000-0000-0000-0000-000000000101',
    '20000000-0000-0000-0000-000000000001',
    '30000000-0000-0000-0000-000000000100',
    'SCEN_OBESITY_PROXY',
    'If formal labs are missing, immediately initiate the Inferred Proxy Protocol. Screen for Acanthosis Nigricans (darkened neck patches) as a diagnostic proxy for high insulin levels/insulin resistance. Screen for frequent night urination (nocturia) and extreme polydipsia to infer impaired fasting glucose thresholds.',
    '{"reasoning": "Allows the digital twin to circumvent missing electronic health records while still generating data points required for initial risk mapping."}'::jsonb,
    'Structural'
),
(
    '60000000-0000-0000-0000-000000000102',
    '20000000-0000-0000-0000-000000000001',
    '30000000-0000-0000-0000-000000000100',
    'SCEN_OBESITY_HBA1C',
    'A fasting blood glucose of 110 mg/dL falls within the 100-125 mg/dL impaired fasting glucose range, signifying prediabetes. If BMI is >= 30 kg/m² simultaneously, categorize as metabolic syndrome threat. Instruct patient to complete a formal HbA1c blood draw to establish baseline stability before prescribing pharmacological interventions.',
    '{"reasoning": "Ensures strict grounding against clinical criteria for prediabetes and metabolic risk classification without prematurely prescribing medical therapies."}'::jsonb,
    'Safety'
),
(
    '60000000-0000-0000-0000-000000000103',
    '20000000-0000-0000-0000-000000000001',
    '30000000-0000-0000-0000-000000000100',
    'SCEN_OBESITY_RED_ZONE',
    'CRITICAL TRIGGER: If an obese or metabolically compromised patient reports localized chest pain, radiating pain down the left arm, or acute shortness of breath (dyspnea), immediately halt the diagnostic interview node, invoke the Human Escalation Trigger skill, flag the session state as RED_ZONE, and instruct the user to seek emergency medical attention.',
    '{"reasoning": "Protects the platform legally and medically by treating cardiorespiratory symptoms in high-risk metabolic profiles as potential acute cardiovascular events."}'::jsonb,
    'Safety'
) ON CONFLICT (id) DO NOTHING;


-- ==========================================
-- PATIENT TWIN STATE SCENARIOS
-- ==========================================
-- Schema: patient_id (UUID), session_id (TEXT), mirror_state (JSONB)
-- We map the user_id, workflow, and task into the JSONB to preserve the data without schema alterations.

CREATE TABLE IF NOT EXISTS patient_twin_state (
    patient_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id   TEXT NOT NULL,
    mirror_state JSONB NOT NULL DEFAULT '{}'::jsonb,
    updated_at   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_patient_twin_session ON patient_twin_state(session_id);

-- SCENARIO 1: The Cold Start / Proxy Mode
INSERT INTO patient_twin_state (patient_id, session_id, mirror_state)
VALUES (
    '70000000-0000-0000-0000-000000000101',
    'session-harini-001',
    '{
        "user_id": "usr-harini-001",
        "current_workflow_id": "30000000-0000-0000-0000-000000000100",
        "current_task_id": "40000000-0000-0000-0000-000000000101",
        "triage_level": "YELLOW_ZONE",
        "confidence_index": 0.45,
        "accumulated_evidence": {
            "height_cm": 165,
            "weight_kg": 95,
            "calculated_bmi": 34.9,
            "bmi_classification": "Class I Obesity",
            "blood_pressure": null,
            "lipid_profile": null,
            "proxies_gathered": {
                "dark_neck_patches": "reported_positive",
                "frequent_night_urination": "reported_positive",
                "string_test_status": "failed"
            }
        },
        "internal_notes": "Patient lacks hard labs. Symptomatic proxies strongly infer underlying insulin resistance and high visceral adiposity. System running in high-probabilistic proxy extraction mode."
    }'::jsonb
) ON CONFLICT (patient_id) DO NOTHING;

-- SCENARIO 2: The Data-Rich / Trend Analysis
INSERT INTO patient_twin_state (patient_id, session_id, mirror_state)
VALUES (
    '70000000-0000-0000-0000-000000000102',
    'session-harini-002',
    '{
        "user_id": "usr-harini-002",
        "current_workflow_id": "30000000-0000-0000-0000-000000000100",
        "current_task_id": "40000000-0000-0000-0000-000000000102",
        "triage_level": "GREEN_ZONE",
        "confidence_index": 0.92,
        "accumulated_evidence": {
            "height_cm": 165,
            "weight_kg": 95,
            "calculated_bmi": 34.9,
            "fasting_blood_sugar": 110,
            "blood_pressure_sys": 138,
            "blood_pressure_dia": 88,
            "hba1c": 5.9,
            "historical_trends": {
                "lipid_profile_2024": "total_chol_180",
                "lipid_profile_2026": "total_chol_210"
            }
        },
        "internal_notes": "Data-rich state achieved via historic records and direct input. Successfully verified Impaired Fasting Glucose (Prediabetes) and Stage 1 Hypertension. Moving to EOSS Stage 2 Synthesis."
    }'::jsonb
) ON CONFLICT (patient_id) DO NOTHING;

-- SCENARIO 3: Serious / Zero Data Escalation
INSERT INTO patient_twin_state (patient_id, session_id, mirror_state)
VALUES (
    '70000000-0000-0000-0000-000000000103',
    'session-harini-003',
    '{
        "user_id": "usr-harini-003",
        "current_workflow_id": "30000000-0000-0000-0000-000000000100",
        "current_task_id": "40000000-0000-0000-0000-000000000101",
        "triage_level": "RED_ZONE",
        "confidence_index": 0.30,
        "accumulated_evidence": {
            "height_cm": 170,
            "weight_kg": 110,
            "calculated_bmi": 38.0,
            "blood_pressure": null,
            "lipid_profile": null,
            "critical_symptoms": ["acute_shortness_of_breath_while_resting"]
        },
        "internal_notes": "Zero formal lab records available, but user triggered major physical safety exception. Bypassing extraction loops to fire an immediate human endocrinologist / clinical triage escalation."
    }'::jsonb
) ON CONFLICT (patient_id) DO NOTHING;

-- SCENARIO 4: Serious / Data-Driven Emergency
INSERT INTO patient_twin_state (patient_id, session_id, mirror_state)
VALUES (
    '70000000-0000-0000-0000-000000000104',
    'session-harini-004',
    '{
        "user_id": "usr-harini-004",
        "current_workflow_id": "30000000-0000-0000-0000-000000000100",
        "current_task_id": "40000000-0000-0000-0000-000000000102",
        "triage_level": "RED_ZONE",
        "confidence_index": 0.95,
        "accumulated_evidence": {
            "height_cm": 160,
            "weight_kg": 105,
            "calculated_bmi": 41.0,
            "hba1c": 8.5,
            "blood_pressure_sys": 165,
            "blood_pressure_dia": 102,
            "critical_symptoms": ["recurrent_chest_pressure_during_mild_movement"]
        },
        "internal_notes": "Patient maps to Morbid Obesity (Class III) with uncontrolled Type 2 Diabetes and Stage 2 Hypertension. Co-occurrence of active chest pressure triggers highest emergency escalation rule."
    }'::jsonb
) ON CONFLICT (patient_id) DO NOTHING;
