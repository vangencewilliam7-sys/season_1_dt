import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from app.services.supabase_client import SupabaseService

db = SupabaseService()
res = db.client.table("document_chunks").select("id, document_id, created_at").order("created_at", desc=True).limit(5).execute()

print("Latest chunks added to DB:")
for r in res.data:
    print(r)
