"""
student_engagement.py — SKL_STUDENT_ENGAGEMENT Functional Skill
===============================================================
Handles AI Tutor day-to-day engagement: instant query resolution,
proactive nudges, and deadline reminders, adapting tone to the 
student's persona.
"""
import os
import json
from typing import Dict, Any
from openai import OpenAI

from app.skills.functional.base_skill import BaseFunctionalSkill

class StudentEngagementSkill(BaseFunctionalSkill):

    @staticmethod
    def skill_name() -> str:
        return "SKL_STUDENT_ENGAGEMENT"

    @staticmethod
    def _generate_persona_system_prompt(persona: str) -> str:
        """
        Returns a system prompt tailored to the student's persona.
        """
        base_prompt = "You are an AI Academic Tutor for a higher-education platform. "
        
        persona_instructions = {
            "BEGINNER": "Use simple words, outline short clear steps, and provide frequent reassurance.",
            "FAST_LEARNER": "Provide concise explanations, ask challenge questions, and avoid repetition.",
            "EXAM_FOCUSED": "Give direct answers, highlight key points, and provide revision checklists.",
            "CAREER_SWITCH": "Focus on practical use-cases and job-oriented examples.",
            "LOW_CONFIDENCE": "Use a highly encouraging tone, celebrate small wins, and keep prompts low-pressure.",
            "DEFAULT": "Maintain a supportive, clear, and professional academic tone."
        }
        
        return base_prompt + persona_instructions.get(persona, persona_instructions["DEFAULT"])

    @staticmethod
    def _build_user_prompt(payload: Dict[str, Any]) -> str:
        """
        Builds the user prompt based on the interaction type and context.
        """
        interaction_type = payload.get("interaction_type")
        query_text = payload.get("query_text")
        context_data = payload.get("context_data", {})
        
        prompt = ""
        
        if interaction_type == "QUERY_RESOLUTION":
            prompt = f"The student has asked the following question:\n'{query_text}'\n\n"
            prompt += "Please provide an immediate, helpful response to resolve their doubt."
            
        elif interaction_type == "PROACTIVE_ENGAGEMENT":
            prompt = "The student has been inactive for several days. "
            if "course_name" in context_data:
                prompt += f"They are currently enrolled in '{context_data['course_name']}'. "
            prompt += "Write a friendly, re-engaging message to check in on them and see if they need help."
            
        elif interaction_type == "DEADLINE_NUDGE":
            prompt = "The student has an upcoming or missed deadline. "
            if "assignment_name" in context_data:
                prompt += f"The assignment is '{context_data['assignment_name']}'. "
            prompt += "Write a supportive nudge to remind them, offering help if they are stuck."
            
        return prompt

    @staticmethod
    def execute(payload: Dict[str, Any]) -> Dict[str, Any]:
        print("\n--- [ORCHESTRATOR] Starting SKL_STUDENT_ENGAGEMENT ---")
        
        student_id = str(payload.get("student_id"))
        persona = payload.get("persona", "DEFAULT")
        interaction_type = payload.get("interaction_type")
        
        # 1. Build prompts
        system_prompt = StudentEngagementSkill._generate_persona_system_prompt(persona)
        user_prompt = StudentEngagementSkill._build_user_prompt(payload)
        
        # Add instructions for structured output to handle triage
        system_prompt += "\n\nYou must return your output strictly in JSON format with two keys:\n"
        system_prompt += "1. 'ai_message': The direct message to the student.\n"
        system_prompt += "2. 'requires_human_escalation': A boolean (true/false). Set to true ONLY if the student expresses extreme frustration, conflict, or asks a question beyond your capability."
        
        # 2. Invoke LLM
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
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            if not content:
                raise Exception("LLM returned empty response")
                
            result_data = json.loads(content)
            ai_message = result_data.get("ai_message", "")
            requires_escalation = result_data.get("requires_human_escalation", False)
            
        except Exception as e:
            print(f"[ORCHESTRATOR] LLM invocation failed: {str(e)}")
            raise Exception(f"Failed to generate tutor response: {str(e)}")
            
        print(f"[ORCHESTRATOR] Engagement processed. Escalation required: {requires_escalation}")
        print("--- [ORCHESTRATOR] Student Engagement complete ---\n")
        
        return {
            "student_id": student_id,
            "interaction_type": interaction_type,
            "persona_applied": persona,
            "tutor_response": ai_message,
            "requires_human_escalation": requires_escalation
        }

    @staticmethod
    def describe_result(result: Dict[str, Any]) -> str:
        esc_str = " (⚠️ Escalated to Human Tutor)" if result.get("requires_human_escalation") else ""
        return f"AI Tutor Response generated for {result.get('interaction_type')} [Persona: {result.get('persona_applied')}]{esc_str}:\n\n> {result.get('tutor_response')}"
