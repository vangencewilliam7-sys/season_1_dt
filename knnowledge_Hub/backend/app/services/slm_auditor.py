import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, Any
from ..models.schemas import SyntheticScenario, AuditResult, MasterCase
from ..models.enums import AuditStatus

load_dotenv()

class SLMAuditor:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            print("Warning: OPENAI_API_KEY not found in environment for SLMAuditor.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini" # Using a fast, high-quality cloud LLM for auditing

    def _call_llm(self, prompt: str) -> Dict[str, Any]:
        """Helper to call OpenAI for auditing."""
        if not self.client:
            return {"status": "Conflict", "feedback": "Cloud LLM Error: No API Key provided."}
            
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a Zero-Trust medical logic auditor. Your goal is to detect hallucinations or logic inconsistencies."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0 # Deterministic for auditing
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error calling Cloud LLM: {e}")
            return {"status": "Conflict", "feedback": f"Cloud LLM Error: {str(e)}"}

    def audit_scenario(self, scenario: SyntheticScenario, source_text: str) -> AuditResult:
        prompt = f"""
        Instructions: Verify if the synthetic scenario is grounded in the source reference. 
        Scenario: "{scenario.scenario_text}"
        Source Reference: "{source_text}"
        
        Criteria:
        1. Does it introduce drugs/conditions NOT in the source?
        2. Is the logic consistent with the source?
        
        Return JSON with:
        {{
            "status": "Pass" or "Conflict",
            "feedback": "Reason for your decision"
        }}
        """
        data = self._call_llm(prompt)
        return AuditResult(
            scenario_id=scenario.id,
            status=AuditStatus.PASS if data.get("status", "").lower() == "pass" else AuditStatus.CONFLICT,
            feedback=data.get("feedback", "No feedback provided")
        )

    def audit_master_case(self, case: MasterCase, transcript: str) -> AuditResult:
        prompt = f"""
        Instructions: Verify if the Parsed Logic matches the Expert Transcript exactly.
        Expert Transcript: "{transcript}"
        Parsed Logic: {json.dumps(case.dict())}
        
        Return JSON with:
        {{
            "status": "Pass" or "Conflict",
            "feedback": "Short reason for your decision"
        }}
        """
        data = self._call_llm(prompt)
        return AuditResult(
            scenario_id=case.scenario_id,
            status=AuditStatus.PASS if data.get("status", "").lower() == "pass" else AuditStatus.CONFLICT,
            feedback=data.get("feedback", "No feedback provided")
        )
