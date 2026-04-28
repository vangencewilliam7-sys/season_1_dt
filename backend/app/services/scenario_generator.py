import os
from openai import OpenAI
from dotenv import load_dotenv
from ..models.schemas import DecisionGap, SyntheticScenario
import json

load_dotenv()

from .context_manager import ContextManager

class ScenarioGenerator:
    def __init__(self, industry: str = "fertility"):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.context_manager = ContextManager(industry=industry)

    def generate_scenario(self, gap: DecisionGap) -> SyntheticScenario:
        if not self.client:
            return SyntheticScenario(
                id=f"scene-{os.urandom(4).hex()}",
                gap_id=gap.id,
                scenario_text="Mock scenario (No API Key)",
                variables={}
            )
            
        ctx = self.context_manager.get_context()
        base_prompt = f"""
        Text snippet from {ctx['domain_name']} documentation: "{gap.ambiguous_text}"
        
        This snippet contains a 'soft rule' or general guideline. Your task as a {ctx['expert_role']} is to create a high-complexity 'Synthetic Scenario' 
        that forces an expert to apply their deep judgment because the 'general rule' might be insufficient.
        
        Requirements:
        1. Create a realistic {ctx['domain_name']} situation.
        2. Introduce 2-3 complicating variables.
        3. The scenario should be grounded in the provided text but push into gray areas.
        
        Return the result in JSON format:
        {{
            "scenario_text": "...",
            "variables": {{ "var1": "...", "var2": "..." }}
        }}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": f"You are a {ctx['expert_role']} representing the highest level of industry expertise."},
                      {"role": "user", "content": base_prompt}],
            response_format={"type": "json_object"}
        )
        
        data = json.loads(response.choices[0].message.content)
        return SyntheticScenario(
            id=f"scene-{os.urandom(4).hex()}",
            gap_id=gap.id,
            scenario_text=data["scenario_text"],
            variables=data["variables"]
        )
