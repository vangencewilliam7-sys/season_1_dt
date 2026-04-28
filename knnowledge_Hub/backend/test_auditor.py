import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.slm_auditor import SLMAuditor
from app.models.schemas import SyntheticScenario, MasterCase
from app.models.enums import AuditStatus

def test_auditor():
    auditor = SLMAuditor()
    
    print("--- Testing Scenario Audit ---")
    scenario = SyntheticScenario(
        id="test-1",
        gap_id="gap-1",
        scenario_text="A patient with stage 4 endometriosis wants to start IVF immediately despite having a high FSH.",
        variables={"stage": "4", "fsh": "high"}
    )
    source_text = "Patients with high FSH should be monitored for 3 months before starting IVF. Endometriosis stage 4 requires surgical consult."
    
    result = auditor.audit_scenario(scenario, source_text)
    print(f"Status: {result.status}")
    print(f"Feedback: {result.feedback}")
    
    print("\n--- Testing Master Case Audit ---")
    case = MasterCase(
        scenario_id="test-1",
        expert_decision="Wait 3 months due to FSH and obtain mandatory surgical consult for stage 4 endometriosis.",
        chain_of_thought=["Identified high FSH requirement", "Identified stage 4 endo requirement", "Combined wait time and consult"],
        logic_tags=["FSH", "Endometriosis", "Surgical Consult"],
        source_chunk_id="chunk-1"
    )
    transcript = "We need to wait for 3 months because of the FSH, and since it's stage 4 endo, a surgical consult is mandatory."
    
    result = auditor.audit_master_case(case, transcript)
    print(f"Status: {result.status}")
    print(f"Feedback: {result.feedback}")

if __name__ == "__main__":
    test_auditor()
