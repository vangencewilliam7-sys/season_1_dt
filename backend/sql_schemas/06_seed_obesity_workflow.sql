-- =============================================================================
-- 06_seed_obesity_workflow.sql
-- Digital Twin Platform — Seed Data for Obesity & Metabolic Diagnosis Workflow
-- =============================================================================
-- Seeds:
--   Workflow → Obesity & Metabolic Diagnosis (Doctor Role)
--   Tasks    → BMI Screening, Physical Proxies Evaluation, Intervention Planning
--   Logic    → Pre-seeded expert_dna records mapping physical proxies to safety thresholds
-- =============================================================================


-- ─────────────────────────────────────────────────────────────────────────────
-- Layer 4: Workflow
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO workflows (id, role_id, name, description)
VALUES (
    '30000000-0000-0000-0000-000000000009',
    '20000000-0000-0000-0000-000000000001',
    'Obesity & Metabolic Diagnosis',
    'Clinical evaluation of obesity, metabolic syndrome, and related physical proxy risk markers.'
)
ON CONFLICT (id) DO NOTHING;


-- ─────────────────────────────────────────────────────────────────────────────
-- Layer 5: Tasks
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO tasks (id, workflow_id, name, description)
VALUES
    ('40000000-0000-0000-0000-000000000021', '30000000-0000-0000-0000-000000000009', 'Calculate BMI & Screen Vitals',          'Determine baseline metabolic metrics and identify low data states.'),
    ('40000000-0000-0000-0000-000000000022', '30000000-0000-0000-0000-000000000009', 'Evaluate Comorbidities & Physical Proxies','Deploy mirror checks (Acanthosis Nigricans) and proxy vitals extraction.'),
    ('40000000-0000-0000-0000-000000000023', '30000000-0000-0000-0000-000000000009', 'Formulate Intervention Plan',            'Synthesise proxy likelihood scores into structured lifestyle and escalation directives.')
ON CONFLICT (id) DO NOTHING;


-- ─────────────────────────────────────────────────────────────────────────────
-- workflow_skills Mapping
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO workflow_skills (workflow_id, skill_id, functional_context_description)
VALUES
    ('30000000-0000-0000-0000-000000000009', '50000000-0000-0000-0000-000000000001', 'Retrieve verified metabolic protocols and proxy markers from the Doctor DNA vault.'),
    ('30000000-0000-0000-0000-000000000009', '50000000-0000-0000-0000-000000000010', 'Synthesise proxy observations and vitals into a structured 4-part clinical layout.'),
    ('30000000-0000-0000-0000-000000000009', '50000000-0000-0000-0000-000000000005', 'Escalate to a human physician if critical markers or severe proxy thresholds are breached.')
ON CONFLICT (workflow_id, skill_id) DO NOTHING;


-- ─────────────────────────────────────────────────────────────────────────────
-- Pre-seeded expert_dna Logic Vault Rules
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO expert_dna (id, scenario_id, expert_decision, impact_archetype, reasoning, domain_id, role_id, workflow_id, task_id)
VALUES
    (
        '60000000-0000-0000-0000-000000000001',
        'METABOLIC_OBESITY_PROXY_01',
        'For patients in a low data state presenting with potential metabolic syndrome or obesity, utilize symptomatic proxies. Acanthosis Nigricans (dark velvety neck patches) indicates high probability of severe insulin resistance. Belt size expansion maps to central visceral adiposity. Recommend immediate laboratory screening (HbA1c, fasting insulin, lipid panel) and frame the assessment around long-term cardiovascular risk.',
        'Safety',
        'Bridging missing objective metrics using validated clinical proxy self-exams guarantees patient safety without premature diagnostic conclusions.',
        '10000000-0000-0000-0000-000000000001',
        '20000000-0000-0000-0000-000000000001',
        '30000000-0000-0000-0000-000000000009',
        '40000000-0000-0000-0000-000000000022'
    )
ON CONFLICT (id) DO NOTHING;
