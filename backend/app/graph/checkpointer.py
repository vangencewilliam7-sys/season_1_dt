import json
from langgraph.checkpoint.base import BaseCheckpointSaver, Checkpoint, CheckpointMetadata
from typing import Optional, Any
from ..services.supabase_client import SupabaseService

class SupabaseCheckpointer(BaseCheckpointSaver):
    """
    A custom LangGraph checkpointer that persists state to the Supabase 'pipeline_state' table.
    """
    def __init__(self):
        super().__init__()
        self.db = SupabaseService()

    def put(self, config: dict, checkpoint: Checkpoint, metadata: CheckpointMetadata, new_versions: dict) -> dict:
        """Save a checkpoint to the database."""
        thread_id = config["configurable"]["thread_id"]
        
        # We store the full checkpoint as JSON in the 'state' column
        state_data = {
            "checkpoint": checkpoint,
            "metadata": metadata,
            "new_versions": new_versions
        }
        
        # Upsert into the pipeline_state table
        self.db.client.table("pipeline_state").upsert({
            "document_id": thread_id,
            "state": state_data,
            "status": "paused_at_socratic" if "interrupt" in str(metadata) else "in_progress",
            "updated_at": "now()"
        }).execute()
        
        return config

    def get_tuple(self, config: dict) -> Optional[Any]:
        """Retrieve a checkpoint from the database."""
        thread_id = config["configurable"]["thread_id"]
        
        res = self.db.client.table("pipeline_state").select("state").eq("document_id", thread_id).execute()
        
        if not res.data:
            return None
            
        data = res.data[0]["state"]
        return (
            config,
            data["checkpoint"],
            data["metadata"],
            None # parent_config
        )

    def list(self, config: Optional[dict] = None, before: Optional[dict] = None, limit: Optional[int] = None):
        """List checkpoints (not strictly required for basic HITL but good for completeness)."""
        return []
