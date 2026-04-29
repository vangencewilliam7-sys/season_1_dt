import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from ..models.schemas import DocumentChunk, MasterCase
from .context_manager import ContextManager

load_dotenv()

class LogicExtractor:
    def __init__(self, industry: str = "fertility"):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.context_manager = ContextManager(industry=industry)

    def extract_logic(self, chunk: DocumentChunk) -> list[MasterCase]:
        if not self.client:
            return []

        ctx = self.context_manager.get_context()
        
        prompt = f"""
        Text from {ctx['domain_name']} documentation:
        "{chunk.content}"
        
        Your task as a {ctx['expert_role']} is to extract definitive 'Expert Logic' from this text.
        A 'Master Case' represents a specific scenario or rule that leads to a clear expert decision.
        
        Instructions:
        1. Identify any clear protocols, "if-then" rules, or diagnostic patterns.
        2. Format each finding as a 'Master Case'.
        3. Ensure the 'expert_decision' is grounded ONLY in the provided text.
        4. Provide a 'chain_of_thought' explaining the logic extracted.
        
        Return the result as a JSON array of objects:
        [
            {{
                "expert_decision": "The action or rule identified",
                "chain_of_thought": ["Reason 1 from text", "Reason 2 from text"],
                "logic_tags": ["Keyword1", "Keyword2"],
                "confidence_note": "How definitive is this rule?"
            }}
        ]
        
        If no clear logic or rules are found, return an empty array [].
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": f"You are a {ctx['expert_role']} extracting structured medical logic."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            # OpenAI response_format json_object requires the output to be a valid JSON object.
            # I asked for an array, but to be safe I'll wrap it or check the key.
            # Let's adjust the prompt slightly to return an object with a "cases" key.
            
            prompt_v2 = prompt.replace("Return the result as a JSON array of objects:", "Return the result as a JSON object with a 'cases' key containing an array of objects:")
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": f"You are a {ctx['expert_role']} extracting structured medical logic."},
                    {"role": "user", "content": prompt_v2}
                ],
                response_format={"type": "json_object"}
            )
            
            data = json.loads(response.choices[0].message.content)
            cases_data = data.get("cases", [])
            
            master_cases = []
            for item in cases_data:
                case = MasterCase(
                    expert_decision=item["expert_decision"],
                    chain_of_thought=item["chain_of_thought"],
                    logic_tags=item["logic_tags"],
                    confidence_note=item.get("confidence_note"),
                    source_chunk_id=chunk.id,
                    scenario_id=f"auto-{os.urandom(4).hex()}" # Placeholder scenario ID
                )
                master_cases.append(case)
                
            return master_cases
        except Exception as e:
            print(f"Error in LogicExtractor: {e}")
            return []
