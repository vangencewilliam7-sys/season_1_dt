import os
import json
import uuid
import datetime
from openai import OpenAI
from dotenv import load_dotenv
from .supabase_client import SupabaseService
from .embeddings import EmbeddingService

load_dotenv(override=True)

class ImplicitIngester:
    """
    SOLID Ingestion Service responsible for processing Human Expert conversation
    threads in the background, identifying new tacit concepts/rules, and dynamically
    committing them to the production Logic Vault (expert_dna) to evolve the Twin.
    """
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.db = SupabaseService()
        self.embedder = EmbeddingService()

    def get_chat_history(self, session_id: str, limit: int = 6) -> str:
        """Helper to fetch recent chat context for the session."""
        if not self.db.client:
            return ""
        try:
            res = self.db.client.table("chat_audit_logs")\
                .select("user_query, final_response, created_at")\
                .eq("session_id", session_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            if not res.data:
                return ""
            
            # Reconstruct chronological conversation
            turns = []
            for log in reversed(res.data):
                user_msg = log.get("user_query", "").strip()
                twin_msg = log.get("final_response", "").strip()
                if user_msg:
                    turns.append(f"User: {user_msg}")
                if twin_msg:
                    turns.append(f"Twin/Expert: {twin_msg}")
            
            return "\n".join(turns)
        except Exception as e:
            print(f"ImplicitIngester: Error fetching history: {e}")
            return ""

    async def ingest_expert_interaction(self, session_id: str, expert_message: str, domain_id: str, role_id: str):
        """
        Background task to extract expert rules from a single interaction
        and insert it into the Supabase 'expert_dna' table.
        """
        if not self.client or not self.db.client:
            print("ImplicitIngester: Client or DB service unavailable.")
            return

        chat_history = self.get_chat_history(session_id)
        
        prompt = f"""
        You are a cognitive engineering extraction node. 
        Your task is to analyze the conversation between the user and a human expert, focusing on the human expert's latest response.
        
        CONVERSATION HISTORY:
        {chat_history}
        
        EXPERT'S LATEST INTERVENTION:
        "{expert_message}"
        
        Analyze this interaction:
        1. Does the expert's response contain a reusable decision rule, clinical diagnostic guideline, academic strategy, or business rule?
        2. If YES, extract it. A high-quality expert rule represents a clear conditional scenario leading to a specific choice (e.g., "If patient presents symptoms A and vitals B, then prescribe C and request check D").
        3. Classify it into one of these archetypes:
           - 'Safety': Direct critical safety boundaries, dosage limits, warning signs, escalation rules.
           - 'Structural': Process-related, protocol benchmarks, standard timelines.
           - 'Informational': Explanatory concepts, definitions, supportive general advice.
        
        Format your response strictly as a JSON object:
        {{
            "has_reusable_rule": true / false,
            "expert_decision": "The clear decision pattern or action guideline identified",
            "impact_archetype": "Safety" / "Structural" / "Informational",
            "reasoning": "Step-by-step reasoning explaining why this is a valid concept to ingest"
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.1,
                messages=[
                    {"role": "system", "content": "You are an expert cognitive psychologist and logic-parsing agent."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            data = json.loads(content if content else "{}")
            
            if not data.get("has_reusable_rule"):
                print("ImplicitIngester: No reusable rule extracted from expert interaction.")
                return

            expert_decision = data.get("expert_decision", "").strip()
            impact_archetype = data.get("impact_archetype", "Informational")
            reasoning = data.get("reasoning", "").strip()
            
            if not expert_decision:
                print("ImplicitIngester: Empty decision logic returned.")
                return
                
            # 1. Generate standard 1536-dim embedding vector
            vector = self.embedder.get_embedding(expert_decision)
            
            # 2. Insert as a permanent DNA rule into 'expert_dna' table
            dna_record = {
                "id": str(uuid.uuid4()),
                "scenario_id": f"implicit-{uuid.uuid4().hex[:6]}",
                "expert_decision": expert_decision,
                "impact_archetype": impact_archetype,
                "reasoning": reasoning,
                "domain_id": domain_id,
                "role_id": role_id,
                "embedding": vector,
                "created_at": datetime.datetime.now().isoformat()
            }
            
            res = self.db.client.table("expert_dna").insert(dna_record).execute()
            print(f"ImplicitIngester: Successfully committed implicitly-learned DNA! ID: {dna_record['id']}")
            return res.data
        except Exception as e:
            print(f"ImplicitIngester: Failed background concept ingestion: {e}")
            return
