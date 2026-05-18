import requests
import json
import uuid

API_BASE = "http://127.0.0.1:8000"

def test_it_prediction(profile_name, payload):
    print(f"\n🚀 Testing IT Scenario: {profile_name}")
    
    req_body = {
        "skill_name": "SKL_IT_PROJECT_PREDICTION",
        "payload": payload,
        "metadata": {
            "workflow_id": str(uuid.uuid4()),
            "expert_id": str(uuid.uuid4())
        }
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/skills/execute/SKL_IT_PROJECT_PREDICTION",
            json=req_body
        )
        print(f"Status Code: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

# Scenario A: The "Healthy" Project
test_it_prediction("The Healthy Sprint", {
    "project_id": str(uuid.uuid4()),
    "velocity_delta": 5.0,
    "requirement_churn": 0.02,
    "dependency_lag_days": 0,
    "qa_failure_rate": 0.05,
    "documentation_completeness": 0.9,
    "team_burnout_risk": 0.1
})

# Scenario B: The "Drifting" Project (High churn & lag)
test_it_prediction("The Drifting Project", {
    "project_id": str(uuid.uuid4()),
    "velocity_delta": -2.0,
    "requirement_churn": 0.25,
    "dependency_lag_days": 5,
    "qa_failure_rate": 0.15,
    "documentation_completeness": 0.6,
    "team_burnout_risk": 0.4
})

# Scenario C: The "Critical" Failure Point (Negative velocity, high burnout)
test_it_prediction("The Critical Failure", {
    "project_id": str(uuid.uuid4()),
    "velocity_delta": -15.0,
    "requirement_churn": 0.40,
    "dependency_lag_days": 10,
    "qa_failure_rate": 0.30,
    "documentation_completeness": 0.4,
    "team_burnout_risk": 0.8
})
