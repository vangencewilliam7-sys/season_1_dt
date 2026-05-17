import os
from typing import Dict
from .supabase_client import SupabaseService

class OverrideService:
    """
    SOLID Service responsible for storing, retrieving, and toggling
    the Active Human Intervention status of interactive sessions.
    
    Includes a robust in-memory dictionary fallback to satisfy Liskov Substitution
    and prevent crashes if the 'session_overrides' DB table has not been created yet.
    """
    _in_memory_overrides: Dict[str, str] = {}

    def __init__(self):
        self.db = SupabaseService()

    def get_status(self, session_id: str) -> str:
        """
        Retrieves override status. 
        Returns 'running' (Twin Active) or 'human_intervention' (Human Active, Twin Silent).
        """
        if not self.db.client:
            return self._in_memory_overrides.get(session_id, "running")
            
        try:
            res = self.db.client.table("session_overrides")\
                .select("status")\
                .eq("session_id", session_id)\
                .execute()
            if res.data:
                return res.data[0]["status"]
            return "running"
        except Exception as e:
            # Safe fallback if SQL query fails (e.g. table not created yet)
            print(f"OverrideService: DB table query failed ({e}). Falling back to in-memory state.")
            return self._in_memory_overrides.get(session_id, "running")

    def set_status(self, session_id: str, status: str) -> bool:
        """
        Updates the override status of a session.
        """
        if status not in ["running", "human_intervention"]:
            raise ValueError(f"Invalid override status value: {status}")

        self._in_memory_overrides[session_id] = status

        if not self.db.client:
            return True

        try:
            self.db.client.table("session_overrides").upsert({
                "session_id": session_id,
                "status": status,
                "updated_at": "now()"
            }).execute()
            return True
        except Exception as e:
            print(f"OverrideService: DB upsert failed ({e}). Cached in-memory successfully.")
            return True
