# Scenario 1: The Cold Start (Proxy Gathering)

### 1. Registration Payload
**Endpoint:** `POST /api/patients/register`
Use this to create a patient who has no clinical labs and relies on "symptomatic proxies."

```json
{
  "full_name": "Michael Chen",
  "email": "michael.chen@example.com",
  "dob": "1978-11-12",
  "gender": "Male",
  "height_cm": 172,
  "weight_kg": 98
}
```

### 2. Clinical Chat Query
**Endpoint:** `POST /api/chat/message`
**Session ID:** Use the `session_id` returned from registration above.

```json
{
  "expert_id": "r1-doctor",
  "session_id": "onboarding- Michael-UUID",
  "message": "I don't have my blood work, but I've noticed my belt size has increased two notches lately and I have these dark, thick patches of skin on the back of my neck. What's happening?",
  "domain": "healthcare",
  "role": "doctor"
}
```

### Expected Behavior:
The Digital Twin should trigger **Proxy Mode**, recognizing "neck patches" (Acanthosis Nigricans) as a surrogate marker for insulin resistance since formal labs are missing.
