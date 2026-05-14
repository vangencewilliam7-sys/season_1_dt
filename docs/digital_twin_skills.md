# Digital Twin Skills Architecture

The Digital Twin's execution capabilities are structured into a powerful two-tier architecture: **Base Skills (B)** and **Functional Skills (F)**. 

- **Base Skills** act as atomic, reusable infrastructure primitives (e.g., "I can send an email").
- **Functional Skills** are composite orchestrations that inject the expert's persona and context into base skills (e.g., "I can send *this expert's* email to *this specific person* about *this contextual event*, matching the expert's exact tone").

---

## 🛠️ Base Skills (B)

Base Skills are the raw, deterministic capabilities that allow the digital twin to interact with external systems. 

### 1. Book Appointment (`book_appointment`)
- **Description:** Books a calendar appointment via an external calendar API.
- **Parameters:** `patient_id`, `appointment_time`, `reason_code`
- **Implementation Map:** `backend/app/skills/wrappers/calendar_service.py`

### 2. Send Communication (`send_communication`)
- **Description:** Dispatches communications (Email/WhatsApp) via external messaging providers.
- **Parameters:** `template_id`, `recipient_address`, `dynamic_vars`
- **Implementation Map:** `backend/app/skills/wrappers/email_service.py`

### 3. Vision OCR (`ACT_VISION_OCR` / `extract_vitals`)
- **Description:** Extracts critical text and metrics from clinical images (e.g., vitals, lab results) using optical character recognition.
- **Parameters:** `image_url`, `extraction_type`
- **Implementation Map:** `backend/app/skills/wrappers/clinical_services.py`

### 4. Report Synthesis (`KNW_REPORT_SYNTHESIS` / `synthesize_report`)
- **Description:** Aggregates and deterministically processes clinical data from multiple diverse sources.
- **Parameters:** `patient_id`, `data_sources`
- **Implementation Map:** `backend/app/skills/wrappers/clinical_services.py`

### 5. Checklist Verify (`ACT_CHECKLIST_VERIFY` / `verify_checklist`)
- **Description:** Audits clinical artifacts and documents to ensure required presence and completeness.
- **Parameters:** `patient_id`, `required_documents`
- **Implementation Map:** `backend/app/skills/wrappers/clinical_services.py`

*(Note: The backend also supports additional primitive wrappers such as `write_to_crm` for logging and `compare_vitals_to_baseline` for numerical bounding).*

---

## 🧠 Functional Skills (F)

Functional Skills orchestrate one or multiple Base Skills into complex workflows, grounding the actions in the expert's `PersonaManifest` and domain history.

### 1. Pre-Op Gatekeeper (`SKL_PRE_OP_GATEKEEPER`)
- **Description:** A multi-step pre-surgery readiness saga. It executes a checklist audit, triggers vitals extraction, and synthesizes a final readiness verdict.
- **Composes:** `ACT_CHECKLIST_VERIFY` + `ACT_VISION_OCR`
- **Parameters:** `patient_id`, `surgery_date`, `required_documents`
- **Implementation Map:** `backend/app/skills/functional/orchestrator.py`

### 2. Expert Synthesis (`SKL_EXPERT_SYNTHESIS`)
- **Description:** A complex 3-step workflow. It aggregates required data, formats an expert clinical brief according to the Persona Manifest, and performs a conditional secure dispatch.
- **Composes:** `KNW_REPORT_SYNTHESIS` + `send_communication`
- **Parameters:** `patient_id`, `data_sources`, `release_approved`
- **Implementation Map:** `backend/app/skills/functional/orchestrator.py`

### 3. Baseline Vigilance (`SKL_BASELINE_VIGILANCE`)
- **Description:** Extracts real-time vitals via OCR, contextually compares them against the patient's historically known baseline thresholds, and flags breaches.
- **Composes:** `ACT_VISION_OCR` (with threshold evaluation logic)
- **Parameters:** `patient_id`, `baseline_thresholds`, `image_url`
- **Implementation Map:** `backend/app/skills/functional/orchestrator.py`

*(Note: Documentation also references educational functional skills like `StudentNotificationSkill` or `CaseEscalationSkill` depending on the domain context of the Twin.)*
