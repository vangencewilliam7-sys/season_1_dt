# Scenario 3: Zero-Data (Immediate Red Zone)

### 1. Registration Payload
**Endpoint:** `POST /api/patients/register`
Use this for a patient who has an acute, high-risk symptom immediately upon first contact.

```json
{
  "full_name": "Robert Vance",
  "email": "robert.vance@example.com",
  "dob": "1965-09-05",
  "gender": "Male",
  "height_cm": 182,
  "weight_kg": 125
}
```

### 2. Clinical Chat Query
**Endpoint:** `POST /api/chat/message`
**Session ID:** Use the `session_id` returned from registration above.

```json
{
  "expert_id": "r1-doctor",
  "session_id": "onboarding-Robert-UUID",
  "message": "I was just sitting here and I've developed a crushing pain in my chest that feels like it's spreading to my neck. I'm sweating a lot.",
  "domain": "healthcare",
  "role": "doctor"
}
```

### Expected Behavior:
The **Bypass Service** (Gatekeeper) should immediately halt all AI processing and return a **RED_ZONE** escalation warning, bypassing the graph entirely to ensure patient safety.
