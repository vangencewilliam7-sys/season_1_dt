# "Green Zone" Safe Testing Scenarios

These scenarios are designed to pass through the **Bypass Gatekeeper** and trigger the actual **Digital Twin AI Logic** (Knowledge Retrieval and Proxy Gathering).

---

## Scenario A: Proxy Gathering (The "Low Data" Path)
**Goal:** Test if the twin identifies missing data and asks for symptomatic proxies.

### 1. Register Patient
```json
{
  "full_name": "Alice Walker",
  "height_cm": 168,
  "weight_kg": 92
}
```

### 2. Chat Query
```json
{
  "expert_id": "r1-doctor",
  "session_id": "onboarding-Alice-UUID",
  "message": "I haven't had a blood test in years, but I'm always thirsty and I've noticed my neck looks a bit dark and dirty even after washing. What could this be?",
  "domain": "healthcare",
  "role": "doctor"
}
```
**Expected AI Result:** `triage_level: YELLOW_ZONE`. The AI should ask for more "proxies" (e.g., about nocturia or family history) because you didn't provide labs.

---

## Scenario B: Knowledge Retrieval (The "Protocol" Path)
**Goal:** Test if the twin retrieves specific metabolic rules from the `expert_dna`.

### 1. Register Patient
```json
{
  "full_name": "David Grant",
  "height_cm": 180,
  "weight_kg": 105
}
```

### 2. Chat Query
```json
{
  "expert_id": "r1-doctor",
  "session_id": "onboarding-David-UUID",
  "message": "My fasting glucose just came back at 112 mg/dL. Based on my BMI, what is my risk level?",
  "domain": "healthcare",
  "role": "doctor"
}
```
**Expected AI Result:** `triage_level: YELLOW_ZONE`. The AI should cite the prediabetes range (100-125 mg/dL) from the expert logic vault.

---

## Scenario C: General Health (The "Standard" Path)
**Goal:** Test standard empathetic interaction.

### 1. Register Patient
```json
{
  "full_name": "Lily Evans",
  "height_cm": 162,
  "weight_kg": 65
}
```

### 2. Chat Query
```json
{
  "expert_id": "r1-doctor",
  "session_id": "onboarding-Lily-UUID",
  "message": "I'm trying to stay healthy. What is considered a healthy BMI for my height?",
  "domain": "healthcare",
  "role": "doctor"
}
```
**Expected AI Result:** `triage_level: GREEN_ZONE`. Standard metabolic advice without emergency triggers.
