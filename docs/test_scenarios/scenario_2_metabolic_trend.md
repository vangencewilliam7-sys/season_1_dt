# Scenario 2: Data-Rich (Metabolic Trend Analysis)

### 1. Registration Payload
**Endpoint:** `POST /api/patients/register`
Use this for a patient who already knows their metabolic markers.

```json
{
  "full_name": "Sarah Miller",
  "email": "sarah.miller@example.com",
  "dob": "1985-02-28",
  "gender": "Female",
  "height_cm": 160,
  "weight_kg": 85
}
```

### 2. Clinical Chat Query
**Endpoint:** `POST /api/chat/message`
**Session ID:** Use the `session_id` returned from registration above.

```json
{
  "expert_id": "r1-doctor",
  "session_id": "onboarding-Sarah-UUID",
  "message": "I just got my labs back. My fasting blood glucose is 115 mg/dL. Given my weight, how concerned should I be about prediabetes?",
  "domain": "healthcare",
  "role": "doctor"
}
```

### Expected Behavior:
The Digital Twin should correlate the **Glucose (115)** with the **BMI (33.2)** and provide grounded metabolic advice from the `expert_dna`, likely flagging this as "Impaired Fasting Glucose."
