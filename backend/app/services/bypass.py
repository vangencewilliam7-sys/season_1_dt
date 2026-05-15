import os
from openai import OpenAI
from dotenv import load_dotenv
from .context_manager import ContextManager

load_dotenv(override=True)

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
        """Deterministic emergency check. No LLM used here to prevent false positives."""
        prompt_lower = prompt.lower()
        
        # 1. Extreme Life-Threat Keywords ONLY
        emergency_triggers = ["suicide", "kill myself", "heart attack", "unconscious"]
        
        for trigger in emergency_triggers:
            if trigger in prompt_lower:
                print(f"--- BYPASS TRIGGERED: {trigger} ---")
                return True
        
        # Everything else is SAFE for the AI Graph
        print(f"--- GATEKEEPER: SAFE ---")
        return False
