import requests
import json
import uuid

API_BASE = "http://127.0.0.1:8000"

def test_monitoring(profile_name, payload):
    print(f"\n🚀 Testing Profile: {profile_name}")
    
    req_body = {
        "skill_name": "SKL_STUDENT_MONITORING",
        "payload": payload,
        "metadata": {
            "workflow_id": str(uuid.uuid4()),
            "expert_id": str(uuid.uuid4())
        }
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/skills/execute/SKL_STUDENT_MONITORING",
            json=req_body
        )
        print(f"Status Code: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

# 1. The "Silent Struggler" (High login, low score, high help delay, declining sentiment)
test_monitoring("The Silent Struggler", {
    "student_id": str(uuid.uuid4()),
    "persona": "LOW_CONFIDENCE",
    "login_frequency": 7,
    "avg_score": 45.5,
    "missed_deadlines": 1,
    "curiosity_coefficient": 0.2,
    "sentiment_trajectory": "DECLINING",
    "help_seeking_delay_days": 8,
    "habit_consistency": 0.95
})

# 2. The "Deep Diver" (Low score, low velocity, but high curiosity)
test_monitoring("The Deep Diver", {
    "student_id": str(uuid.uuid4()),
    "persona": "CAREER_SWITCH",
    "login_frequency": 4,
    "avg_score": 62.0,
    "missed_deadlines": 0,
    "curiosity_coefficient": 0.9,
    "sentiment_trajectory": "STABLE",
    "help_seeking_delay_days": 1,
    "habit_consistency": 0.7
})
