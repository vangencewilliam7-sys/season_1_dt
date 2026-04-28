# Implementation Plan — Phase 2: Divergence Engine & Scenario Generation

The goal of Phase 2 is to move from static document search to **active logic extraction**. We will identify "Decision Gaps" in the source documents and synthesize test scenarios that will be presented to the expert later.

## User Review Required

> [!IMPORTANT]
> **LLM Usage**: This phase heavily relies on LLM calls. We will use `gpt-4o` for high-reasoning scenario generation and `gpt-4o-mini` (the SLM) for the deterministic audit to keep costs low.
> **Prompt Engineering**: The quality of extraction depends entirely on the prompts. I will implement a "Chain-of-Thought" prompting strategy for scenario generation.

## Proposed Changes

### 1. Intelligence Services

#### [NEW] [divergence_scanner.py](file:///c:/Users/harin/Downloads/knowledge_hub/backend/app/services/divergence_scanner.py)
A service that uses regex and LLM scanning to identify semantic markers (e.g., "typically", "generally", "consider"). It flags these as `DecisionGap` objects.

#### [NEW] [scenario_generator.py](file:///c:/Users/harin/Downloads/knowledge_hub/backend/app/services/scenario_generator.py)
Takes a `DecisionGap` and the source context to generate a multi-variable `SyntheticScenario`. 
- Logic: "The text says X is typical. Create a scenario where X might NOT apply (e.g., patient has contraindications A and B)."

#### [NEW] [slm_auditor.py](file:///c:/Users/harin/Downloads/knowledge_hub/backend/app/services/slm_auditor.py)
A specialized service using a smaller model (SLM) to perform the **Hallucination Pre-Filter**. It verifies that the generated scenario is grounded in the source text and hasn't hallucinated new medical drugs or conditions.

### 2. Pipeline Node Implementation

#### [MODIFY] [divergence.py](file:///c:/Users/harin/Downloads/knowledge_hub/backend/app/graph/nodes/divergence.py)
Implement the node logic:
1. Iterate over `raw_chunks`.
2. Scan for gaps.
3. Generate scenarios for each gap.
4. Update `GraphState`.

#### [MODIFY] [slm_filter.py](file:///c:/Users/harin/Downloads/knowledge_hub/backend/app/graph/nodes/slm_filter.py)
Implement the node logic:
1. Audit each scenario.
2. Filter out failed scenarios.
3. Update `GraphState` with `slm_audit_results`.

---

## Verification Plan

### Automated Tests
- `backend/tests/test_divergence.py`: Verify that "typically" markers are correctly identified in sample text.
- `backend/tests/test_scenario_grounding.py`: Verify that the SLM auditor correctly catches a scenario containing a drug not mentioned in the source doc.

### Manual Verification
1. Run the pipeline on the `Business Overview.txt`.
2. Inspect the `synthetic_scenarios` in the graph state.
3. Confirm that scenarios are clinically complex but grounded in the business logic defined in the doc.
