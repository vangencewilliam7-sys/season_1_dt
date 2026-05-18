"""
Diagnose the exact Supabase RPC issues by querying the DB metadata.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from app.services.supabase_client import SupabaseService
db = SupabaseService()

print("="*60)
print("DIAGNOSIS 1: document_chunks table — id column type")
print("="*60)

try:
    # Query the information_schema to get the actual column type
    res = db.client.rpc("", {}).execute()  # won't work, let's use raw SQL via rpc
except:
    pass

# Instead, let's just fetch one row and inspect
try:
    res = db.client.table("document_chunks").select("id").limit(1).execute()
    if res.data:
        sample_id = res.data[0]["id"]
        print(f"Sample ID value: {sample_id}")
        print(f"Python type: {type(sample_id)}")
        print(f"Looks like UUID? {len(str(sample_id)) == 36 and '-' in str(sample_id)}")
    else:
        print("No rows in document_chunks")
except Exception as e:
    print(f"Error: {e}")

print()
print("="*60)
print("DIAGNOSIS 2: Check document_chunks schema via select")
print("="*60)

# Let's see what columns exist
try:
    res = db.client.table("document_chunks").select("*").limit(1).execute()
    if res.data:
        print(f"Columns: {list(res.data[0].keys())}")
        row = res.data[0]
        for col, val in row.items():
            if col == "embedding":
                print(f"  {col}: [vector of length {len(val) if val else 0}]")
            elif col == "content":
                print(f"  {col}: {str(val)[:80]}...")
            else:
                print(f"  {col}: {val} (type: {type(val).__name__})")
    else:
        print("No rows")
except Exception as e:
    print(f"Error: {e}")

print()
print("="*60)
print("DIAGNOSIS 3: expert_dna table schema")
print("="*60)

try:
    res = db.client.table("expert_dna").select("*").limit(1).execute()
    if res.data:
        print(f"Columns: {list(res.data[0].keys())}")
        row = res.data[0]
        for col, val in row.items():
            if col == "embedding":
                print(f"  {col}: [vector of length {len(val) if val else 0}]")
            elif col == "expert_decision":
                print(f"  {col}: {str(val)[:80]}...")
            else:
                print(f"  {col}: {val} (type: {type(val).__name__})")
    else:
        print("No rows")
except Exception as e:
    print(f"Error: {e}")

print()
print("="*60)
print("DIAGNOSIS 4: Try calling match_chunks with explicit column cast")
print("="*60)

try:
    dummy_vec = [0.0] * 1536
    res = db.client.rpc("match_chunks", {
        "query_embedding": dummy_vec,
        "match_threshold": 0.0,
        "match_count": 1
    }).execute()
    print(f"SUCCESS: {res.data}")
except Exception as e:
    print(f"FAILED: {e}")

print()
print("="*60)
print("DIAGNOSIS 5: Try calling match_expert_dna with all 5 params")
print("="*60)

try:
    dummy_vec = [0.0] * 1536
    res = db.client.rpc("match_expert_dna", {
        "query_embedding": dummy_vec,
        "match_threshold": 0.0,
        "match_count": 1,
        "p_domain_id": None,
        "p_workflow_id": None
    }).execute()
    print(f"SUCCESS with 5 params: {len(res.data)} results")
except Exception as e:
    print(f"FAILED with 5 params: {e}")

# Try the 3-param version explicitly
try:
    dummy_vec = [0.0] * 1536
    res = db.client.rpc("match_expert_dna", {
        "query_embedding": dummy_vec,
        "match_threshold": 0.4,
        "match_count": 1
    }).execute()
    print(f"SUCCESS with 3 params: {len(res.data)} results")
except Exception as e:
    print(f"FAILED with 3 params: {e}")
