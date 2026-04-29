import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class GuardrailService:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.model = "gpt-4o-mini" # Fast model for gatekeeping

    def verify_coverage(self, query: str, expert_logic: str) -> bool:
        """
        Verifies if the expert_logic explicitly covers the user's query.
        Returns True if safe to answer, False otherwise.
        """
        if not self.client:
            return False
            
        prompt = f"""
        User Query: "{query}"
        Provided Expert Logic: "{expert_logic}"
        
        Instructions:
        Determine if the User Query can be answered COMPLETELY and ACCURATELY using ONLY the Provided Expert Logic.
        
        Strict Rules:
        1. If the logic is general but the query is specific, return FALSE.
        2. If the answer requires any clinical knowledge NOT in the Provided Expert Logic, return FALSE.
        3. If the logic is a protocol for X but the query is about Y, return FALSE.
        
        Return ONLY the word "TRUE" or "FALSE".
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a Zero-Trust Medical Guardrail. Your only job is to detect if a query is 'Out of Bounds' for the provided knowledge."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )
            result = response.choices[0].message.content.strip().upper()
            return "TRUE" in result
        except Exception as e:
            print(f"Guardrail Error: {e}")
            return False
