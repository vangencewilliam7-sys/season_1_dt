from ...models.state import GraphState
from ...services.divergence_scanner import DivergenceScanner
from ...services.scenario_generator import ScenarioGenerator
from ...services.context_manager import ContextManager
from ...models.schemas import AuditEntry
import datetime

def divergence_node(state: GraphState) -> GraphState:
    # Load industry context
    context_manager = ContextManager() 
    ctx = context_manager.get_context()
    
    print(f"--- DIVERGENCE: Scanning {len(state.raw_chunks)} chunks for {ctx['domain_name']} ---")
    
    scanner = DivergenceScanner()
    # Inject industry-specific markers into the scanner
    scanner.markers = ctx['semantic_markers']
    
    generator = ScenarioGenerator()
    
    new_gaps = []
    new_scenarios = []
    
    for chunk in state.raw_chunks:
        gaps = scanner.scan_text(chunk.content, chunk.id)
        for gap in gaps:
            new_gaps.append(gap)
            # Generate scenario with domain jacket
            scenario = generator.generate_scenario(gap)
            new_scenarios.append(scenario)
            
    state.decision_gaps.extend(new_gaps)
    state.synthetic_scenarios.extend(new_scenarios)
    
    state.audit_log.append(AuditEntry(
        node="divergence",
        timestamp=datetime.datetime.now().isoformat(),
        action="Gaps and Scenarios generated",
        details=f"Found {len(new_gaps)} gaps and created {len(new_scenarios)} scenarios."
    ))
    
    return state
