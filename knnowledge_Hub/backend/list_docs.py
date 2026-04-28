import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def list_all_docs():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        print("Missing credentials")
        return

    try:
        supabase: Client = create_client(url, key)
        # Group by document_id and count chunks
        # Supabase client doesn't support group by directly in select, but we can do a query
        res = supabase.table("document_chunks").select("document_id, created_at").execute()
        
        counts = {}
        for item in res.data:
            doc_id = item["document_id"]
            counts[doc_id] = counts.get(doc_id, 0) + 1
            
        print("--- All Document IDs in Database ---")
        for doc_id, count in counts.items():
            print(f"ID: {doc_id} | Chunks: {count}")
            
        if not counts:
            print("No documents found in 'document_chunks' table.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_all_docs()
