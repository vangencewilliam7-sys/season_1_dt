import httpx
import json

def test_onboarding():
    url = "http://localhost:8000/api/patients/register"
    
    payload = {
        "full_name": "John Doe",
        "email": "john.doe@example.com",
        "dob": "1985-06-15",
        "gender": "Male",
        "height_cm": 180,
        "weight_kg": 95
    }
    
    print(f"--- Registering New Patient: {payload['full_name']} ---")
    
    try:
        response = httpx.post(url, json=payload, timeout=10.0)
        if response.status_code == 200:
            data = response.json()
            print("Status: SUCCESS")
            print(f"Patient ID: {data['patient_id']}")
            print(f"Calculated BMI: {data['base_bmi']}")
            print(f"Session ID: {data['session_id']}")
            print(f"Message: {data['message']}")
        else:
            print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_onboarding()
