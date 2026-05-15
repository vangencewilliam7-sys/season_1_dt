"""
project_prediction.py — SKL_IT_PROJECT_PREDICTION Functional Skill
==================================================================
Simulates project launch risks and generates 'Pre-Mortem' analysis to
prevent project failure before it occurs.
"""
import os
import json
from typing import Dict, Any
from openai import OpenAI

from app.skills.functional.base_skill import BaseFunctionalSkill

class ItProjectPredictionSkill(BaseFunctionalSkill):

    @staticmethod
    def skill_name() -> str:
        return "SKL_IT_PROJECT_PREDICTION"

    @staticmethod
    def _calculate_failure_probability(payload: Dict[str, Any]) -> int:
        """
        Calculates a probability of project delay (0-100%).
        """
        risk = 0
        
        # 1. Velocity Delta (Negative delta = high risk)
        v_delta = payload.get("velocity_delta", 0)
        if v_delta < -10: risk += 30
        elif v_delta < 0: risk += 15
        
        # 2. Requirement Churn (High churn = high risk)
        churn = payload.get("requirement_churn", 0)
        risk += min(int(churn * 100), 30)
        
        # 3. Dependency Lag
        lag = payload.get("dependency_lag_days", 0)
        risk += min(lag * 5, 20)
        
        # 4. Burnout & QA
        risk += int(payload.get("team_burnout_risk", 0) * 10)
        risk += int(payload.get("qa_failure_rate", 0) * 10)
            
        return min(risk, 100)

    @staticmethod
    def execute(payload: Dict[str, Any]) -> Dict[str, Any]:
        print("\n--- [ORCHESTRATOR] Starting SKL_IT_PROJECT_PREDICTION ---")
        
        project_id = str(payload.get("project_id"))
        failure_prob = ItProjectPredictionSkill._calculate_failure_probability(payload)
        
        # Pre-Mortem Logic
        system_prompt = f"""You are the CTO-level Digital Twin Analyst.
Your goal is to perform a 'Pre-Mortem' analysis on a software project.
Assume the project has FAILED in the future, and now you are explaining WHY it happened and how to fix it NOW.

PROJECT METRICS:
- Failure Probability: {failure_prob}%
- Velocity Change: {payload.get('velocity_delta')}%
- Requirement Churn: {payload.get('requirement_churn', 0)*100}%
- Dependency Lag: {payload.get('dependency_lag_days', 0)} days
- Team Burnout Risk: {payload.get('team_burnout_risk', 0)}
- QA Failure Rate: {payload.get('qa_failure_rate', 0)*100}%

ANALYSIS FRAMEWORK:
1. **The Future Autopsy**: Describe the specific scenario where this project fails (e.g., 'A cascading delay in the API layer caused a 2-week launch slip').
2. **The Root Cause**: Identify the primary metric driving this risk.
3. **Strategic Mitigation**: Provide exactly one bold, high-level instruction to the Project Manager to save the project.

Return your response in JSON format:
{{
    "failure_scenario": "Description of the future failure.",
    "root_cause_analysis": "Identification of the key risk factor.",
    "mitigation_action": "The single bold action to take now.",
    "mitigation_rationale": "Why this specific action will work."
}}
"""
        
        user_prompt = f"Analyze project {project_id} and provide the Pre-Mortem briefing."

        try:
            api_key = os.environ.get("OPENAI_API_KEY")
            client = OpenAI(api_key=api_key)
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            raw_content = response.choices[0].message.content
            if not raw_content:
                raise Exception("LLM returned empty content")
            content = json.loads(raw_content)
            
        except Exception as e:
            print(f"[ORCHESTRATOR] LLM invocation failed: {str(e)}")
            content = {
                "failure_scenario": "Critical data pipeline collapse.",
                "root_cause_analysis": "Unknown error in risk simulation.",
                "mitigation_action": "Pause all non-essential features and audit the critical path.",
                "mitigation_rationale": "Safety-first stabilization."
            }
            
        print(f"[ORCHESTRATOR] IT Prediction complete. Risk: {failure_prob}%")
        print("--- [ORCHESTRATOR] IT Prediction complete ---\n")
        
        return {
            "project_id": project_id,
            "failure_probability": failure_prob,
            "scenario": content.get("failure_scenario"),
            "root_cause": content.get("root_cause_analysis"),
            "next_best_action": content.get("mitigation_action"),
            "rationale": content.get("mitigation_rationale")
        }

    @staticmethod
    def describe_result(result: Dict[str, Any]) -> str:
        icon = "🚨" if result['failure_probability'] > 60 else "⚠️" if result['failure_probability'] > 30 else "✅"
        return (
            f"{icon} **Project Risk Forecast: {result['failure_probability']}% Failure Probability**\n\n"
            f"**Future Autopsy:** {result['scenario']}\n\n"
            f"**Root Cause:** {result['root_cause']}\n\n"
            f"**🎯 Strategic Mitigation:** {result['next_best_action']}\n\n"
            f"*Rationale:* {result['rationale']}"
        )
