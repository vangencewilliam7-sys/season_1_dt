-- =============================================================================
-- 05_seed_presales_domain.sql
-- Digital Twin Platform — Seed Data for Pre-Sales Domain
-- =============================================================================
-- Run this AFTER 04_seed_domains_and_roles.sql
--
-- Seeds:
--   1 Domain  → Pre-Sales
--   1 Role    → Architect
--   2 Workflows + 5 Tasks
--   3 Functional Skill Definitions
--
-- UUID Convention for NEW domains:
--   Domain IDs:   10000000-0000-0000-0000-00000000000N  (N = 4, 5, 6...)
--   Role IDs:     20000000-0000-0000-0000-00000000000N  (N = 4, 5, 6...)
--   Workflow IDs:  30000000-0000-0000-0000-00000000000N  (N = 7, 8, 9...)
--   Task IDs:     40000000-0000-0000-0000-00000000000N  (N = 16, 17, 18...)
--   Skill IDs:    50000000-0000-0000-0000-00000000000N  (N = 40, 41, 42...)
-- =============================================================================


-- ─────────────────────────────────────────────────────────────────────────────
-- Layer 2: Domain
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO domains (id, hub_id, name, description)
VALUES (
    '10000000-0000-0000-0000-000000000004',
    '00000000-0000-0000-0000-000000000001',
    'Pre-Sales',
    'Client discovery, technical solutioning, and proposal engineering domain.'
)
ON CONFLICT (id) DO NOTHING;


-- ─────────────────────────────────────────────────────────────────────────────
-- Layer 3: Role
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO roles (id, domain_id, name, description)
VALUES (
    '20000000-0000-0000-0000-000000000004',
    '10000000-0000-0000-0000-000000000004',
    'Architect',
    'Solutions Architect responsible for technical discovery and proposal design.'
)
ON CONFLICT (id) DO NOTHING;


-- ─────────────────────────────────────────────────────────────────────────────
-- Layer 4: Workflows
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO workflows (id, role_id, name, description)
VALUES
    (
        '30000000-0000-0000-0000-000000000007',
        '20000000-0000-0000-0000-000000000004',
        'Technical Discovery',
        'End-to-end client discovery from initial requirement capture to architecture proposal.'
    ),
    (
        '30000000-0000-0000-0000-000000000008',
        '20000000-0000-0000-0000-000000000004',
        'Proposal Engineering',
        'Crafting technical proposals, SOWs, and effort estimates based on discovery findings.'
    )
ON CONFLICT (id) DO NOTHING;


-- ─────────────────────────────────────────────────────────────────────────────
-- Layer 5: Tasks
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO tasks (id, workflow_id, name, description)
VALUES
    ('40000000-0000-0000-0000-000000000016', '30000000-0000-0000-0000-000000000007', 'Infer Client Tech Stack',        'Analyse public data (website, LinkedIn, job postings) to determine current technology landscape.'),
    ('40000000-0000-0000-0000-000000000017', '30000000-0000-0000-0000-000000000007', 'Match Reference Architectures',  'Compare client requirements against proven internal reference projects.'),
    ('40000000-0000-0000-0000-000000000018', '30000000-0000-0000-0000-000000000007', 'Generate Discovery Brief',       'Synthesise findings into a structured pre-sales briefing note.'),
    ('40000000-0000-0000-0000-000000000019', '30000000-0000-0000-0000-000000000008', 'Draft Technical Proposal',       'Create a solution architecture document with component diagrams and integration points.'),
    ('40000000-0000-0000-0000-000000000020', '30000000-0000-0000-0000-000000000008', 'Estimate Effort & Timeline',     'Produce T-shirt sizing and timeline estimates based on reference project actuals.')
ON CONFLICT (id) DO NOTHING;


-- ─────────────────────────────────────────────────────────────────────────────
-- Skills Engine: Pre-Sales Skill Definitions
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO skill_definitions (id, skill_name, skill_type, is_active, requires_human_approval)
VALUES
    ('50000000-0000-0000-0000-000000000040', 'Tech Stack Inference',       'Functional', true, false),
    ('50000000-0000-0000-0000-000000000041', 'Reference Architecture Match','Functional', true, false),
    ('50000000-0000-0000-0000-000000000042', 'Discovery Brief Generation', 'Functional', true, true)
ON CONFLICT (id) DO NOTHING;


-- ─────────────────────────────────────────────────────────────────────────────
-- workflow_skills: Map Skills to Workflows
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO workflow_skills (workflow_id, skill_id, functional_context_description)
VALUES
    ('30000000-0000-0000-0000-000000000007', '50000000-0000-0000-0000-000000000001', 'Retrieve relevant past project architectures and client case studies from the Pre-Sales DNA vault.'),
    ('30000000-0000-0000-0000-000000000007', '50000000-0000-0000-0000-000000000040', 'Infer the client current technology landscape from public data sources.'),
    ('30000000-0000-0000-0000-000000000007', '50000000-0000-0000-0000-000000000041', 'Match client requirements against internal reference architectures to identify re-usable patterns.'),
    ('30000000-0000-0000-0000-000000000008', '50000000-0000-0000-0000-000000000042', 'Generate a structured discovery brief with tech stack analysis and recommended architecture.')
ON CONFLICT (workflow_id, skill_id) DO NOTHING;
