import httpx
import json
import asyncio

async def test_expert():
    url = "http://localhost:8000/api/chat/message"
    
    test_cases = [
        {
            "name": "RED ZONE: Acute Emergency",
            "payload": {
                "expert_id": "r1-doctor",
                "session_id": "test-session-red",
                "message": "I am having severe chest pain and radiating pain in my left arm.",
                "domain": "healthcare",
                "role": "doctor"
            }
        },
        {
            "name": "LOW DATA: Proxy Gathering",
            "payload": {
                "expert_id": "r1-doctor",
                "session_id": "test-session-proxy",
                "message": "I don't know my blood pressure or glucose, but I've noticed dark velvety patches on my neck and I'm thirsty all the time.",
                "domain": "healthcare",
                "role": "doctor"
            }
        },
        {
            "name": "KNOWLEDGE: Standard Metabolic Advice",
            "payload": {
                "expert_id": "r1-doctor",
                "session_id": "test-session-knowledge",
                "message": "My fasting glucose is 110 mg/dL and my BMI is 34. What does this mean?",
                "domain": "healthcare",
                "role": "doctor"
            }
        }
    ]

    async with httpx.AsyncClient(timeout=30.0) as client:
        for case in test_cases:
            print(f"\n--- Testing: {case['name']} ---")
            print(f"Message: {case['payload']['message']}")
            try:
                response = await client.post(url, json=case['payload'])
                if response.status_code == 200:
                    data = response.json()
                    print(f"Triage Level: {data.get('triage_level')}")
                    print(f"Response:\n{data.get('response')}")
                    print(f"Rationale: {data.get('rationale')}")
                else:
                    print(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                print(f"Request failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_expert())
