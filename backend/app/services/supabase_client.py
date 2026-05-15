import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseService:
    def __init__(self):
        url: str | None = os.environ.get("SUPABASE_URL")
        key: str | None = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            print("Warning: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found in environment.")
            self.client = None
        else:
            self.client: Client = create_client(url, key)

    def insert_chunks(self, chunks: list[dict]):
        if not self.client: return
        return self.client.table("document_chunks").insert(chunks).execute()

    def semantic_search(self, embedding: list[float], limit: int = 5):
        if not self.client: return []
        response = self.client.rpc("match_chunks", {
            "query_embedding": embedding,
            "match_threshold": 0.5,
            "match_count": limit
        }).execute()
        return response.data

    def insert_expert_dna(self, data: dict):
        """Final commit of expert-verified logic into the production vault."""
        if not self.client: return
        return self.client.table("expert_dna").insert(data).execute()

    def expert_vault_search(
        self,
        embedding: list[float],
        domain_id: str | None = None,
        workflow_id: str | None = None,
        limit: int = 1,
    ):
        """
        High-purity search against verified expert logic only.

        Args:
            embedding:   Query vector from EmbeddingService.
            domain_id:   Optional FK from the `domains` table.
            workflow_id: Optional FK from the `workflows` table.
            limit:       Max results to return.
        """
        if not self.client: return []

        try:
            # Pass filters natively to the updated RPC to guarantee DB-level isolation
            query = self.client.rpc("match_expert_dna", {
                "query_embedding": embedding,
                "match_threshold": 0.40,
                "match_count": limit,
                "p_domain_id": domain_id,
                "p_workflow_id": workflow_id
            })

            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Supabase RPC match_expert_dna failed: {e}. Returning empty list.")
            return []

    def insert_chat_audit_log(self, data: dict):
        """Logs the LangGraph chat execution trace to the database."""
        if not self.client: return
        return self.client.table("chat_audit_logs").insert(data).execute()

    def update_patient_twin_state(self, session_id: str, mirror_data: dict):
        """Upserts persistent diagnostic confidence and triage state mirrors."""
        if not self.client: return
        try:
            res = self.client.table("patient_twin_state").select("patient_id").eq("session_id", session_id).execute()
            if res.data:
                return self.client.table("patient_twin_state").update({
                    "mirror_state": mirror_data
                }).eq("session_id", session_id).execute()
            else:
                return self.client.table("patient_twin_state").insert({
                    "session_id": session_id,
                    "mirror_state": mirror_data
                }).execute()
        except Exception as e:
            print(f"Error updating patient twin state mirror: {e}")

    def get_count(self, table: str) -> int:
        """Returns the total row count for a given table."""
        if not self.client: return 0
        try:
            # We use a select with head=True to just get the count
            response = self.client.table(table).select("*", count="exact").limit(0).execute()
            return response.count if response.count is not None else 0
        except Exception as e:
            print(f"Error fetching count for {table}: {e}")
            return 0

