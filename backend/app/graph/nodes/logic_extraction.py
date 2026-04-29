from ...models.state import GraphState
from ...services.logic_extractor import LogicExtractor
from ...models.schemas import AuditEntry
import datetime

def logic_extraction_node(state: GraphState) -> GraphState:
    print(f"--- LOGIC EXTRACTION: Extracting Master Cases from {len(state.raw_chunks)} chunks ---")
    
    extractor = LogicExtractor()
    all_extracted_cases = []
    
    # To avoid excessive API calls in prototype, we'll focus on chunks with high content volume 
    # or specific markers, but for now let's process top 5 chunks.
    # Actually, let's process all but stop if we get enough.
    
    for chunk in state.raw_chunks:
        cases = extractor.extract_logic(chunk)
        if cases:
            all_extracted_cases.extend(cases)
        
        if len(all_extracted_cases) >= 5: # Limit for prototype
            break
            
    state.parsed_cases.extend(all_extracted_cases)
    
    state.audit_log.append(AuditEntry(
        node="logic_extraction",
        timestamp=datetime.datetime.now().isoformat(),
        action="Automatic logic extraction complete",
        details=f"Extracted {len(all_extracted_cases)} master cases directly from document."
    ))
    
    return state
