"""
scripts/demo_run.py

End-to-end demonstration of the Persona Extraction Framework.
Uses the 'Tech Consulting' adapter and the 'Mock LLM' provider.

Steps:
1. Loads expert documents from data/expert_archi_001/
2. Builds the LangGraph extraction pipeline
3. Executes Ingestion -> Journalist -> Compiler nodes
4. Displays the final PersonaManifest
"""

import sys
import os
import json
import logging
from uuid import uuid4

# Add project root to sys.path
sys.path.append(os.getcwd())

from core.graph import build_extraction_graph, create_initial_state
from adapters.tech_consulting.tech_consulting_adapter import TechConsultingAdapter
from providers.mock_llm import MockLLMProvider
from runtime.readers.filesystem_reader import FilesystemReader

# Configure logging to see the pipeline progress
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("Demo")

def run_demo():
    logger.info("=== STARTING PERSONA EXTRACTION DEMO ===")
    
    expert_id = "expert_archi_001"
    
    # 1. Initialize Reader & Load Documents
    logger.info(f"Step 1: Reading documents for expert: {expert_id}")
    reader = FilesystemReader(base_dir="data")
    documents = reader.load(expert_id)
    
    if not documents:
        logger.error(f"No documents found in data/{expert_id}. Please run 'mkdir -p' and create sample files first.")
        return

    doc_dicts = [doc.to_dict() for doc in documents]
    logger.info(f"Loaded {len(documents)} documents.")

    # 2. Setup Dependencies (Tech Consulting + Mock LLM)
    logger.info("Step 2: Initializing Tech Consulting Adapter and Mock LLM")
    adapter = TechConsultingAdapter()
    
    # We use MockLLM for both steps to avoid needing an API Key
    llm = MockLLMProvider(model_id="llama-3.1-70b-mock")

    # 3. Build & Run Graph
    logger.info("Step 3: Compiling extraction graph...")
    graph = build_extraction_graph(
        llm_ingestion=llm,
        llm_journalist=llm,
        adapter=adapter
    )

    initial_state = create_initial_state(
        expert_id=str(uuid4()),
        domain=adapter.get_domain_id(),
        documents=doc_dicts,
        identity_override={
            "name": "Alex Rivet",
            "role": "Principal Solutions Architect"
        }
    )

    logger.info("Step 4: Executing extraction pipeline (Ingestion -> Journalist -> Compile)...")
    final_state = graph.invoke(initial_state)

    if final_state.get("error"):
        logger.error(f"Extraction failed: {final_state['error']}")
        return

    # 5. Result
    logger.info("=== EXTRACTION COMPLETE ===")
    
    manifest_json = final_state.get("final_manifest")
    if manifest_json:
        manifest = json.loads(manifest_json)
        logger.info("Successfully generated PersonaManifest:")
        print(json.dumps(manifest, indent=2))
        
        # Save to output file
        output_file = f"output_manifest_{expert_id}.json"
        with open(output_file, "w") as f:
            f.write(manifest_json)
        logger.info(f"Manifest saved to {output_file}")
    else:
        logger.warning("No manifest was produced.")

if __name__ == "__main__":
    run_demo()
