"""
scripts/export_prompt.py

Utility to convert a structured PersonaManifest into a 
high-fidelity System Prompt for LLMs.
"""

import json
import sys
import os

def generate_prompt(manifest_str: str) -> str:
    manifest = json.loads(manifest_str)
    
    identity = manifest['identity']
    style = manifest['communication_style']
    heuristics = manifest['heuristics']
    drop_zones = manifest['drop_zone_triggers']

    prompt = f"SYSTEM PROMPT: {identity['name'].upper()} ({identity['role'].upper()})\n"
    prompt += "="*60 + "\n\n"
    
    prompt += "### IDENTITY & ROLE\n"
    prompt += f"You are {identity['name']}, a {identity['role']} specializing in {identity['domain'].replace('_', ' ')}.\n"
    prompt += f"Your goal is to provide high-leverage advice based on your specific professional heuristics.\n\n"

    prompt += "### COMMUNICATION STYLE\n"
    prompt += f"- Tone: {', '.join(style['tone'])}\n"
    prompt += f"- Verbosity: {style['verbosity']}\n"
    prompt += f"- Critical Framing: {style['preferred_framing']}\n\n"

    prompt += "### EXPERT HEURISTICS (Your Decision Engine)\n"
    for i, h in enumerate(heuristics):
        prompt += f"{i+1}. SCENARIO: {h['trigger']}\n"
        prompt += f"   DECISION: {h['decision']}\n"
        prompt += f"   REASONING: {h['reasoning']}\n\n"

    prompt += "### KNOWLEDGE BOUNDARIES (DROP ZONES)\n"
    prompt += "If the conversation drifts into the following topics, you MUST stop and escalate to a human colleague:\n"
    for dz in drop_zones:
        prompt += f"- {dz}\n"
    
    prompt += "\n" + "="*60 + "\n"
    prompt += "Execute all responses with the precision and skepticism of a senior consultant."
    
    return prompt

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.export_prompt <job_id>")
        return

    job_id = sys.argv[1]
    jobs_path = "data/jobs.json"

    if not os.path.exists(jobs_path):
        print("No jobs found.")
        return

    with open(jobs_path, "r") as f:
        jobs = json.load(f)

    job = jobs.get(job_id)
    if not job:
        print(f"Job {job_id} not found.")
        return

    print("\n" + generate_prompt(job['final_manifest']))

if __name__ == "__main__":
    main()
