import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def check_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    print(f"URL: {url}")
    # print(f"KEY: {key[:10]}...") 
    
    if not url or not key:
        print("Missing credentials")
        return

    try:
        supabase: Client = create_client(url, key)
        # Check if the doc id exists
        target_id = "502591d3-e531-4ff1-88e3-8a63805c82df"
        res = supabase.table("document_chunks").select("id").eq("document_id", target_id).execute()
        print(f"Chunks found for {target_id}: {len(res.data)}")
        
        # Check total count
        res_total = supabase.table("document_chunks").select("id", count="exact").execute()
        print(f"Total chunks in 'document_chunks': {res_total.count}")
        
        # List any document IDs present
        res_docs = supabase.table("document_chunks").select("document_id").limit(10).execute()
        doc_ids = set(r["document_id"] for r in res_docs.data)
        print(f"Sample Document IDs in DB: {doc_ids}")

    except Exception as e:
        print(f"Error connecting to Supabase: {e}")

if __name__ == "__main__":
    check_supabase()
