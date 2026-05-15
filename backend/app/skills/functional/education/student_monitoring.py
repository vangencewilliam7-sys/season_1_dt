"""
student_monitoring.py — SKL_STUDENT_MONITORING Functional Skill
==============================================================
Performs Deep Intelligence analysis on student behavioral patterns to 
calculate risk levels and suggest Next Best Actions (NBA) for human tutors.
"""
import os
import json
from typing import Dict, Any
from openai import OpenAI

from app.skills.functional.base_skill import BaseFunctionalSkill

class StudentMonitoringSkill(BaseFunctionalSkill):

    @staticmethod
    def skill_name() -> str:
        return "SKL_STUDENT_MONITORING"

    @staticmethod
    def _calculate_base_risk(payload: Dict[str, Any]) -> int:
        """
        Calculates a numeric risk score (0-100) based on raw metrics.
        """
        score = 0
        
        # 1. Login Frequency (Max 20 points)
        logins = payload.get("login_frequency", 0)
        if logins < 2: score += 20
        elif logins < 4: score += 10
        
        # 2. Avg Score (Max 30 points)
        avg_score = payload.get("avg_score", 100)
        if avg_score < 50: score += 30
        elif avg_score < 70: score += 15
        
        # 3. Missed Deadlines (Max 30 points)
        missed = payload.get("missed_deadlines", 0)
        score += min(missed * 10, 30)
        
        # 4. Deep Metrics (Max 20 points)
        if payload.get("sentiment_trajectory") == "DECLINING":
            score += 10
        if payload.get("help_seeking_delay_days", 0) > 5:
            score += 10
            
        return min(score, 100)

    @staticmethod
    def execute(payload: Dict[str, Any]) -> Dict[str, Any]:
        print("\n--- [ORCHESTRATOR] Starting SKL_STUDENT_MONITORING ---")
        
        student_id = str(payload.get("student_id"))
        base_risk = StudentMonitoringSkill._calculate_base_risk(payload)
        
        # Triage Classification
        triage_level = "LOW"
        if base_risk > 70: triage_level = "HIGH"
        elif base_risk > 30: triage_level = "MEDIUM"
        
        # Deep Intelligence Analysis & NBA Generation
        system_prompt = f"""You are the Expert Analyst node of an Educational Digital Twin.
Your goal is to analyze a student's 'Deep Intelligence' metrics and provide a strategic briefing for a human tutor.

STUDENT METRICS:
- Risk Score: {base_risk}/100
- Triage Level: {triage_level}
- Curiosity Coefficient: {payload.get('curiosity_coefficient')} (Depth of questions)
- Sentiment Trajectory: {payload.get('sentiment_trajectory')}
- Habit Consistency: {payload.get('habit_consistency')}
- Help-Seeking Delay: {payload.get('help_seeking_delay_days')} days

ANALYSIS FRAMEWORK:
1. **Findings**: What are the most critical patterns?
2. **Interpretation**: What does this say about the student's psychological state or momentum?
3. **Synthesis**: Connect multiple metrics (e.g., High curiosity + declining sentiment).
4. **Next Best Action (NBA)**: Provide exactly one concrete, actionable instruction for the human tutor.

Return your response in JSON format:
{{
    "analysis_synthesis": "Your expert summary of the student's state.",
    "next_best_action": "The single most important step the human tutor should take.",
    "intervention_reasoning": "Why this action is the most effective choice."
}}
"""
        
        user_prompt = f"Analyze the following student profile (ID: {student_id}) and provide the Next Best Action."

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
                temperature=0.4
            )
            
            content = json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"[ORCHESTRATOR] LLM invocation failed: {str(e)}")
            content = {
                "analysis_synthesis": "Automated analysis failed. Manual review required.",
                "next_best_action": "Reach out to the student for a general check-in.",
                "intervention_reasoning": "Default fallback due to analysis error."
            }
            
        print(f"[ORCHESTRATOR] Monitoring complete. Triage: {triage_level}")
        print("--- [ORCHESTRATOR] Student Monitoring complete ---\n")
        
        return {
            "student_id": student_id,
            "risk_score": base_risk,
            "triage_level": triage_level,
            "analysis": content.get("analysis_synthesis"),
            "next_best_action": content.get("next_best_action"),
            "intervention_reasoning": content.get("intervention_reasoning")
        }

    @staticmethod
    def describe_result(result: Dict[str, Any]) -> str:
        color = "🔴" if result['triage_level'] == "HIGH" else "🟡" if result['triage_level'] == "MEDIUM" else "🟢"
        return (
            f"{color} **Student Risk Assessment: {result['triage_level']}** (Score: {result['risk_score']}/100)\n\n"
            f"**Synthesis:** {result['analysis']}\n\n"
            f"**🎯 Next Best Action:** {result['next_best_action']}\n\n"
            f"*Reasoning:* {result['intervention_reasoning']}"
        )
