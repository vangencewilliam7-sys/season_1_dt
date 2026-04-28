import os
from openai import OpenAI
from dotenv import load_dotenv
from .context_manager import ContextManager

load_dotenv()

class BypassService:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        
        # Load local context
        self.context_manager = ContextManager()
        ctx = self.context_manager.get_context()
        self.emergency_keywords = ctx['risk_keywords']
        self.role = ctx['expert_role']

    def check_risk(self, prompt: str) -> bool:
        # 1. Keyword check (Fast, deterministic)
        prompt_lower = prompt.lower()
        if any(keyword in prompt_lower for keyword in self.emergency_keywords):
            return True
            
        # 2. LLM Risk Assessment (Nuanced)
        if not self.client: return False
        
        assessment = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are a risk triage engine for {self.role}. Respond only with 'SAFE' or 'BYPASS'."},
                {"role": "user", "content": f"Does this query require immediate human expert intervention? Query: {prompt}"}
            ]
        )
        risk = assessment.choices[0].message.content.strip().upper()
        if risk == "BYPASS":
            print(f"--- EMERGENCY BYPASS: LLM detected clinical risk ---")
            return True
            
        return False
