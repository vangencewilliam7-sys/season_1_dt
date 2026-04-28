from ...models.state import GraphState
from ...models.schemas import MasterCase, AuditEntry
from ...services.context_manager import ContextManager
from openai import OpenAI
import os
import json
import datetime

def parser_node(state: GraphState) -> GraphState:
    # Load industry context
    context_manager = ContextManager()
    ctx = context_manager.get_context()
    
    print(f"--- PARSER: Extracting {ctx['domain_name']} logic from {len(state.expert_transcripts)} transcripts ---")
    
    api_key = os.environ.get("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key) if api_key else None
    
    new_cases = []
    
    for transcript in state.expert_transcripts:
        if not client:
            # Mock parsing
            case = MasterCase(
                expert_decision=f"Mock Decision ({ctx['domain_name']})",
                chain_of_thought=["Mock step 1"],
                logic_tags=[ctx['industry']],
                source_chunk_id="mock-chunk",
                scenario_id=transcript.scenario_id
            )
        else:
            prompt = f"""
            Context: {ctx['domain_name']}
            Expert Role: {ctx['expert_role']}
            
            Expert Transcript: "{transcript.raw_text}"
            
            Deconstruct this {ctx['expert_role']} response into a structured logic record.
            
            Return JSON:
            {{
                "expert_decision": "The final deterministic action stated",
                "chain_of_thought": ["step 1", "step 2", "step 3"],
                "logic_tags": ["tag1", "tag2"],
                "confidence_note": "..."
            }}
            """
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": "You are a senior logic extractor."},
                          {"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            
            # Find original chunk ID via scenario_id
            scenario = next((s for s in state.synthetic_scenarios if s.id == transcript.scenario_id), None)
            gap = next((g for g in state.decision_gaps if g.id == scenario.gap_id), None) if scenario else None
            source_id = gap.source_chunk_id if gap else "unknown"

            case = MasterCase(
                expert_decision=data["expert_decision"],
                chain_of_thought=data["chain_of_thought"],
                logic_tags=data["logic_tags"],
                confidence_note=data.get("confidence_note"),
                source_chunk_id=source_id,
                scenario_id=transcript.scenario_id
            )
        new_cases.append(case)
        
    state.parsed_cases.extend(new_cases)
    
    state.audit_log.append(AuditEntry(
        node="parser",
        timestamp=datetime.datetime.now().isoformat(),
        action="Logic extraction complete",
        details=f"Parsed {len(new_cases)} master cases."
    ))
    
    return state
