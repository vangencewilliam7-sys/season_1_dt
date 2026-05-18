"""
Pipeline Verification Script
=============================
Tests each stage of the Knowledge Ingestion Pipeline independently
to identify exactly what works and what doesn't.
"""
import os
import sys

# Ensure we can import from app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

results = []

def report(stage, status, detail=""):
    icon = "[OK]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[WARN]"
    results.append((stage, status, detail))
    print(f"{icon} [{status}] {stage}: {detail}")


# ─────────────────────────────────────────────────────
# STAGE 1: File Parsing (HierarchicalParser)
# ─────────────────────────────────────────────────────
print("\n" + "="*60)
print("STAGE 1: FILE PARSING (HierarchicalParser)")
print("="*60)

try:
    from app.services.parser import HierarchicalParser
    parser = HierarchicalParser()

    # Test DOCX parsing
    sample_docx = os.path.join(os.path.dirname(__file__), "..", "..", "sample_documents", "embryo_transfer_guidelines.docx")
    if os.path.exists(sample_docx):
        chunks = parser.parse_docx(sample_docx)
        if chunks and len(chunks) > 0:
            report("DOCX Parsing", "PASS", f"{len(chunks)} chunks extracted from embryo_transfer_guidelines.docx")
            # Show first chunk preview
            print(f"   First chunk preview: {chunks[0]['content'][:100]}...")
            print(f"   Chunk keys: {list(chunks[0].keys())}")
            # Check hierarchy
            has_hierarchy = any(c['level'] > 0 for c in chunks)
            report("DOCX Hierarchy Detection", "PASS" if has_hierarchy else "WARN", 
                   f"Heading levels found: {set(c['level'] for c in chunks)}")
        else:
            report("DOCX Parsing", "FAIL", "No chunks returned")
    else:
        report("DOCX Parsing", "WARN", f"Sample file not found: {sample_docx}")

    # Test PDF parsing with an uploaded file
    upload_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
    pdf_files = [f for f in os.listdir(upload_dir) if f.endswith('.pdf')] if os.path.exists(upload_dir) else []
    if pdf_files:
        pdf_path = os.path.join(upload_dir, pdf_files[0])
        pdf_chunks = parser.parse_pdf(pdf_path)
        if pdf_chunks and len(pdf_chunks) > 0:
            report("PDF Parsing", "PASS", f"{len(pdf_chunks)} chunks from {pdf_files[0][:30]}...")
            print(f"   First chunk preview: {pdf_chunks[0]['content'][:100]}...")
        else:
            report("PDF Parsing", "FAIL", "No chunks returned from PDF")
    else:
        report("PDF Parsing", "WARN", "No PDF files found in uploads/")

except Exception as e:
    report("File Parsing", "FAIL", str(e))


# ─────────────────────────────────────────────────────
# STAGE 2: PII Scrubber
# ─────────────────────────────────────────────────────
print("\n" + "="*60)
print("STAGE 2: PII SCRUBBER")
print("="*60)

try:
    from app.services.pii_scrubber import PIIScrubber
    scrubber = PIIScrubber()

    test_text = "Patient Jane contacted Dr. Smith at jane@clinic.com on 12/05/2025"
    scrubbed = scrubber.scrub(test_text)
    has_pii = "jane@clinic.com" in scrubbed
    report("PII Scrubbing", "FAIL" if has_pii else "PASS", 
           f"Original: '{test_text[:50]}...' → Scrubbed: '{scrubbed[:80]}...'")

    # Test restore
    restored = scrubber.restore(scrubbed)
    report("PII Restore", "PASS" if "jane@clinic.com" in restored else "FAIL",
           f"Restored: '{restored[:80]}...'")

except Exception as e:
    report("PII Scrubber", "FAIL", str(e))


# ─────────────────────────────────────────────────────
# STAGE 3: Embedding Service
# ─────────────────────────────────────────────────────
print("\n" + "="*60)
print("STAGE 3: EMBEDDING SERVICE")
print("="*60)

try:
    from app.services.embeddings import EmbeddingService
    embedder = EmbeddingService()

    if embedder.client:
        test_embedding = embedder.get_embedding("Test medical text about fertility treatment")
        if test_embedding and len(test_embedding) == 1536:
            report("Single Embedding", "PASS", f"Vector dimension: {len(test_embedding)}, first 3 values: {test_embedding[:3]}")
        else:
            report("Single Embedding", "FAIL", f"Unexpected embedding: len={len(test_embedding) if test_embedding else 0}")

        # Batch test
        batch = embedder.get_embeddings_batch(["Text A", "Text B", "Text C"])
        if batch and len(batch) == 3 and all(len(v) == 1536 for v in batch):
            report("Batch Embeddings", "PASS", f"3 vectors, each dim=1536")
        else:
            report("Batch Embeddings", "FAIL", f"Unexpected batch result")
    else:
        report("Embedding Service", "FAIL", "OpenAI client not initialized — OPENAI_API_KEY missing")

except Exception as e:
    report("Embedding Service", "FAIL", str(e))


# ─────────────────────────────────────────────────────
# STAGE 4: Supabase Connection + Tables
# ─────────────────────────────────────────────────────
print("\n" + "="*60)
print("STAGE 4: SUPABASE CONNECTION")
print("="*60)

try:
    from app.services.supabase_client import SupabaseService
    db = SupabaseService()

    if db.client:
        # Check document_chunks table
        try:
            res = db.client.table("document_chunks").select("id", count="exact").limit(0).execute()
            chunk_count = res.count if res.count is not None else 0
            report("document_chunks Table", "PASS", f"{chunk_count} rows exist")
        except Exception as e:
            report("document_chunks Table", "FAIL", str(e))

        # Check expert_dna table
        try:
            res = db.client.table("expert_dna").select("id", count="exact").limit(0).execute()
            dna_count = res.count if res.count is not None else 0
            report("expert_dna Table", "PASS", f"{dna_count} rows exist")
        except Exception as e:
            report("expert_dna Table", "FAIL", str(e))

        # Check match_chunks RPC
        try:
            dummy_vec = [0.0] * 1536
            res = db.client.rpc("match_chunks", {
                "query_embedding": dummy_vec,
                "match_threshold": 0.0,
                "match_count": 1
            }).execute()
            report("match_chunks RPC", "PASS", f"Returned {len(res.data)} results")
        except Exception as e:
            report("match_chunks RPC", "FAIL", str(e))

        # Check match_expert_dna RPC
        try:
            res = db.client.rpc("match_expert_dna", {
                "query_embedding": dummy_vec,
                "match_threshold": 0.0,
                "match_count": 1
            }).execute()
            report("match_expert_dna RPC", "PASS", f"Returned {len(res.data)} results")
        except Exception as e:
            report("match_expert_dna RPC", "FAIL", str(e))
    else:
        report("Supabase Connection", "FAIL", "Client not initialized — missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")

except Exception as e:
    report("Supabase Connection", "FAIL", str(e))


# ─────────────────────────────────────────────────────
# STAGE 5: Divergence Scanner
# ─────────────────────────────────────────────────────
print("\n" + "="*60)
print("STAGE 5: DIVERGENCE SCANNER")
print("="*60)

try:
    from app.services.divergence_scanner import DivergenceScanner
    scanner = DivergenceScanner()

    # Text WITH soft language
    test_text_with_gap = "In most cases, patients typically respond to gonadotropin stimulation within 7-10 days, but some may require extended protocols."
    gaps = scanner.scan_text(test_text_with_gap, "test-chunk-1")
    report("Soft Language Detection", "PASS" if len(gaps) > 0 else "FAIL",
           f"Found {len(gaps)} gaps in text with 'typically' and 'most cases'")

    # Text WITHOUT soft language
    test_text_no_gap = "Administer 150 IU FSH on Day 2 of the cycle."
    gaps2 = scanner.scan_text(test_text_no_gap, "test-chunk-2")
    report("Clean Text (No False Positives)", "PASS" if len(gaps2) == 0 else "WARN",
           f"Found {len(gaps2)} gaps in deterministic text")

except Exception as e:
    report("Divergence Scanner", "FAIL", str(e))


# ─────────────────────────────────────────────────────
# STAGE 6: Context Manager
# ─────────────────────────────────────────────────────
print("\n" + "="*60)
print("STAGE 6: CONTEXT MANAGER")
print("="*60)

try:
    from app.services.context_manager import ContextManager
    cm = ContextManager()
    ctx = cm.get_context()
    report("Fertility Context", "PASS" if ctx.get("domain_name") else "FAIL",
           f"Domain: {ctx.get('domain_name')}, Role: {ctx.get('expert_role')}, Markers: {len(ctx.get('semantic_markers', []))}")

    cm_legal = ContextManager(industry="legal")
    ctx2 = cm_legal.get_context()
    report("Legal Context", "PASS" if ctx2.get("domain_name") == "Corporate Law Compliance" else "FAIL",
           f"Domain: {ctx2.get('domain_name')}")

except Exception as e:
    report("Context Manager", "FAIL", str(e))


# ─────────────────────────────────────────────────────
# STAGE 7: LangGraph Pipeline Compilation
# ─────────────────────────────────────────────────────
print("\n" + "="*60)
print("STAGE 7: LANGGRAPH PIPELINE COMPILATION")
print("="*60)

try:
    from app.graph.pipeline import create_pipeline
    pipeline = create_pipeline()
    report("Pipeline Compilation", "PASS", f"Graph compiled successfully. Type: {type(pipeline).__name__}")

    # Check nodes are registered
    node_names = list(pipeline.nodes.keys()) if hasattr(pipeline, 'nodes') else []
    report("Pipeline Nodes", "PASS" if len(node_names) >= 6 else "FAIL",
           f"Registered nodes: {node_names}")

except Exception as e:
    report("Pipeline Compilation", "FAIL", str(e))


# ─────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────
print("\n" + "="*60)
print("SUMMARY")
print("="*60)

passed = sum(1 for _, s, _ in results if s == "PASS")
failed = sum(1 for _, s, _ in results if s == "FAIL")
warned = sum(1 for _, s, _ in results if s == "WARN")

print(f"\n  PASSED: {passed}")
print(f"  FAILED: {failed}")
print(f"  WARNINGS: {warned}")
print(f"  Total: {len(results)}")

if failed > 0:
    print("\n  FAILED STAGES:")
    for stage, status, detail in results:
        if status == "FAIL":
            print(f"    [FAIL] {stage}: {detail}")
