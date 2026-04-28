from ...models.state import GraphState
from ...services.slm_auditor import SLMAuditor
from ...models.schemas import AuditEntry
from ...models.enums import AuditStatus
import datetime

def audit_node(state: GraphState) -> GraphState:
    print(f"--- AUDIT: Performing Echo Verification on {len(state.parsed_cases)} master cases ---")
    
    auditor = SLMAuditor()
    audit_results = []
    
    # Map scenario IDs to raw transcripts for audit reference
    transcript_map = {t.scenario_id: t.raw_text for t in state.expert_transcripts}
    
    for case in state.parsed_cases:
        transcript = transcript_map.get(case.scenario_id, "")
        result = auditor.audit_master_case(case, transcript)
        audit_results.append(result)
        
    # If any fail, we might need to retry (handled by conditional edge logic which we'd add in a production iteration)
    # For now, we'll log them and proceed to the Expert Gate
    conflicts = [r for r in audit_results if r.status == AuditStatus.CONFLICT]
    
    state.audit_log.append(AuditEntry(
        node="visual_audit",
        timestamp=datetime.datetime.now().isoformat(),
        action="Echo Verification complete",
        details=f"Audited {len(audit_results)} cases. {len(conflicts)} conflicts detected."
    ))
    
    return state
