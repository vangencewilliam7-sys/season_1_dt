import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv(override=True)

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
        """
        if not self.client: return []
        try:
            query = self.client.rpc("match_expert_dna", {
                "query_embedding": embedding,
                "match_threshold": 0.35,
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

    def create_patient(self, data: dict):
        """Creates a new patient record in the registry."""
        if not self.client: return
        return self.client.table("patients").insert(data).execute()

    def get_patient(self, patient_id: str):
        """Retrieves a patient record by ID."""
        if not self.client: return None
        res = self.client.table("patients").select("*").eq("id", patient_id).execute()
        return res.data[0] if res.data else None

    def update_patient_notes(self, patient_id: str, note_entry: dict):
        """Appends a new clinical note to the patient's record."""
        if not self.client: return
        # Get existing notes first
        res = self.client.table("patients").select("clinical_notes").eq("id", patient_id).execute()
        notes = res.data[0].get("clinical_notes", []) if res.data else []
        notes.append(note_entry)
        
        return self.client.table("patients").update({
            "clinical_notes": notes
        }).eq("id", patient_id).execute()

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

    def get_pipeline_status(self, session_id: str) -> str:
        """Gets the status of the pipeline state for a session."""
        if not self.client: return "in_progress"
        try:
            res = self.client.table("pipeline_state").select("status").eq("document_id", session_id).execute()
            if res.data:
                return res.data[0].get("status", "in_progress")
            return "in_progress"
        except Exception as e:
            print(f"Error fetching pipeline status: {e}")
            return "in_progress"

    def update_pipeline_status(self, session_id: str, status: str):
        """Updates the status of the pipeline state for a session."""
        if not self.client: return
        try:
            # We must upsert in case the session hasn't been saved yet. But pipeline_state needs a 'state' jsonb.
            # Usually the checkpointer creates it first. Let's just update for now.
            res = self.client.table("pipeline_state").select("document_id").eq("document_id", session_id).execute()
            if res.data:
                return self.client.table("pipeline_state").update({"status": status}).eq("document_id", session_id).execute()
            else:
                # If it doesn't exist, we might have to create a blank state. This is rare unless override triggered before first chat.
                return self.client.table("pipeline_state").insert({
                    "document_id": session_id,
                    "state": {},
                    "status": status
                }).execute()
        except Exception as e:
            print(f"Error updating pipeline status: {e}")

    # --- Storage / Bucket Methods ---

    def upload_document(self, file_bytes: bytes, file_path: str, bucket_name: str = "knowledge-base-docs") -> dict:
        """Uploads a file to a Supabase bucket."""
        if not self.client: return {"error": "Supabase client not initialized"}
        try:
            # Try to get the file first to overwrite or just upload
            response = self.client.storage.from_(bucket_name).upload(
                file=file_bytes,
                path=file_path,
                file_options={"upsert": "true", "content-type": "application/octet-stream"}
            )
            return {"path": file_path, "response": response}
        except Exception as e:
            print(f"Error uploading document: {e}")
            return {"error": str(e)}

    def download_document(self, file_path: str, bucket_name: str = "knowledge-base-docs") -> bytes:
        """Downloads a file from a Supabase bucket into memory."""
        if not self.client: raise Exception("Supabase client not initialized")
        try:
            return self.client.storage.from_(bucket_name).download(file_path)
        except Exception as e:
            print(f"Error downloading document: {e}")
            raise

    def get_document_url(self, file_path: str, bucket_name: str = "knowledge-base-docs", expires_in: int = 3600) -> str:
        """Generates a secure signed URL for temporary file access."""
        if not self.client: return ""
        try:
            response = self.client.storage.from_(bucket_name).create_signed_url(file_path, expires_in)
            return response.get("signedURL", "")
        except Exception as e:
            print(f"Error getting signed URL: {e}")
            return ""

    def list_documents(self, prefix: str = "", bucket_name: str = "knowledge-base-docs") -> list:
        """Lists files in the bucket, optionally filtering by prefix."""
        if not self.client: return []
        try:
            return self.client.storage.from_(bucket_name).list(path=prefix)
        except Exception as e:
            print(f"Error listing documents: {e}")
            return []
