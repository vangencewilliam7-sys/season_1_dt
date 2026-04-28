from ...models.state import GraphState
from ...services.slm_auditor import SLMAuditor
from ...models.schemas import AuditEntry
from ...models.enums import AuditStatus
import datetime

def slm_filter_node(state: GraphState) -> GraphState:
    print(f"--- SLM FILTER: Auditing {len(state.synthetic_scenarios)} scenarios ---")
    
    auditor = SLMAuditor()
    new_audit_results = []
    
    # Map chunk IDs to content for auditor reference
    chunk_map = {c.id: c.content for c in state.raw_chunks}
    
    for scenario in state.synthetic_scenarios:
        # Find the source gap
        gap = next((g for g in state.decision_gaps if g.id == scenario.gap_id), None)
        if not gap: continue
        
        source_text = chunk_map.get(gap.source_chunk_id, "")
        result = auditor.audit_scenario(scenario, source_text)
        new_audit_results.append(result)
        
    state.slm_audit_results = new_audit_results
    
    # Check for conflicts - if any fail, we might need to retry (handled by conditional edge)
    conflicts = [r for r in new_audit_results if r.status == AuditStatus.CONFLICT]
    if conflicts:
        state.retry_count += 1
        print(f"Audit found {len(conflicts)} conflicts. Retry count: {state.retry_count}")
    
    state.audit_log.append(AuditEntry(
        node="slm_filter",
        timestamp=datetime.datetime.now().isoformat(),
        action="Audit complete",
        details=f"Audited {len(new_audit_results)} scenarios. {len(conflicts)} conflicts found."
    ))
    
    return state
