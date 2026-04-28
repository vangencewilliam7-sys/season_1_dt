"""
scripts/seed_jobs.py

Helper to populate the extraction job store with dummy data.
Ensures the Shadow Mode Dashboard has content to show even before 
the first real extraction is run.
"""

import os
import json
import uuid
from datetime import datetime

JOBS_FILE = "d:/Expert-Persona/data/jobs.json"

def seed():
    os.makedirs(os.path.dirname(JOBS_FILE), exist_ok=True)
    
    # Example Manifest
    manifest = {
        "expert_id": "expert_archi_001",
        "extracted_at": datetime.now().isoformat(),
        "manifest_version": 1,
        "source_documents": ["architecture_principles.md", "scaling_ecommerce.md"],
        "identity": {
            "name": "Alex Rivet",
            "role": "Principal Solutions Architect",
            "domain": "tech_consulting"
        },
        "communication_style": {
            "tone": ["direct", "pragmatic", "skeptical of hype"],
            "verbosity": "concise",
            "preferred_framing": "Risk-first evaluation"
        },
        "heuristics": [
            {
                "trigger": "When a performance bottleneck exists in a legacy DB during a time-sensitive period",
                "decision": "Use redis caching/buffering instead of a DB migration",
                "reasoning": "Stability is more important than the 'perfect' DB when deadlines are short"
            },
            {
                "trigger": "When presented with a legacy migration request",
                "decision": "Force decomposition of the monolith into serverless/modern components",
                "reasoning": "Migration is the ONLY time you have political leverage to fix architectural debt"
            }
        ],
        "drop_zone_triggers": ["Frontend Frameworks", "Mobile UX design"],
        "confidence_threshold": 0.94,
        "shadow_approved": False
    }

    job_id = "demo-job-" + str(uuid.uuid4())[:8]
    
    jobs = {}
    if os.path.exists(JOBS_FILE):
        with open(JOBS_FILE, "r") as f:
            jobs = json.load(f)

    jobs[job_id] = {
        "job_id": job_id,
        "expert_id": "expert_archi_001",
        "status": "complete",
        "current_node": None,
        "error": None,
        "final_manifest": json.dumps(manifest),
        "compilation_issues": ["Only 2 heuristics extracted (minimum 3 recommended)"]
    }

    with open(JOBS_FILE, "w") as f:
        json.dump(jobs, f, indent=2)

    print(f"Successfully seeded Job ID: {job_id}")

if __name__ == "__main__":
    seed()
