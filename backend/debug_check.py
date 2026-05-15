import os
import traceback
from dotenv import load_dotenv
load_dotenv()

def debug():
    print("--- DEBUG START ---")
    
    # 1. Check Env
    print(f"OPENAI_API_KEY set: {bool(os.environ.get('OPENAI_API_KEY'))}")
    print(f"PII_ENCRYPTION_KEY set: {bool(os.environ.get('PII_ENCRYPTION_KEY'))}")
    
    # 2. Test Scrubber
    try:
        from app.services.pii_scrubber import PIIScrubber
        scrubber = PIIScrubber()
        scrubbed = scrubber.scrub("Test message for Dr. Smith")
        print(f"Scrubber Test: SUCCESS | {scrubbed}")
    except Exception:
        print("Scrubber Test: FAILED")
        traceback.print_exc()

    # 3. Test Adapter
    try:
        from app.adapters import get_adapter
        adapter = get_adapter("healthcare", "doctor")
        print(f"Adapter Test: SUCCESS | {adapter.get_domain_name()}")
    except Exception:
        print("Adapter Test: FAILED")
        traceback.print_exc()

    # 4. Test Bypass Service
    try:
        from app.services.bypass import BypassService
        bypass = BypassService()
        risk = bypass.check_risk("Normal query")
        print(f"Bypass Test (Safe): SUCCESS | Risk={risk}")
    except Exception:
        print("Bypass Test: FAILED")
        traceback.print_exc()

    # 5. Test Supabase
    try:
        from app.services.supabase_client import SupabaseService
        db = SupabaseService()
        count = db.get_count("expert_dna")
        print(f"Supabase Test: SUCCESS | expert_dna count={count}")
    except Exception:
        print("Supabase Test: FAILED")
        traceback.print_exc()

if __name__ == "__main__":
    debug()
