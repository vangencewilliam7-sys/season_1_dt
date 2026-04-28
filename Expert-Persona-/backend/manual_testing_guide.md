# Manual Testing Guide: Universal Persona Extraction Framework

This guide provides a structured 10-case testing plan to validate the high-fidelity extraction of your Expert Personas.

## 📋 The Test Suite (10 Cases)

### 🟢 Easy Cases (Baseline Validity)
1. **The Resume Scan**: Use a simple PDF/MD resume.
   - *Goal*: Verify Identity (Name, Role) and Communication Style extraction.
2. **The "Best Practice" List**: Use a document containing a bulleted list of "My Rules for X".
   - *Goal*: Ensure heuristics are captured exactly as written.
3. **Single Success Story**: Use one clearly written Master Case.
   - *Goal*: Verify the "Conflict -> Decision -> Result" extraction chain.

### 🟡 Middle Cases (Logic & Integration)
4. **The Noise Test**: Provide a document where 50% is irrelevant chatter (e.g., meeting transcripts).
   - *Goal*: Test the Ingestion Node's ability to filter out "Noise" and find "Signals."
5. **The Failure Case**: Provide a case study about a project that **failed**.
   - *Goal*: Verify if the AI extracts the "Reasoning" (What was learned?) as a heuristic.
6. **Multi-Source Read**: Place documents in both a local folder and simulated API.
   - *Goal*: Validate the Framework's ability to consolidate knowledge from different readers.

### 🔴 Hard Cases (Boundary & Logic Stress)
7. **The Contradiction**: Provide two documents that give opposite advice for the same problem.
   - *Goal*: See how the `JournalistNode` handles ambiguity—does it flag a quality warning?
8. **The Domain Switch**: Use an expert from a completely new industry (e.g., *Gourmet Chef*).
   - *Goal*: Test the "Generic Adapter"'s flexibility for unconfigured domains.
9. **The Knowledge Wall**: Provide a document that explicitly says "I never handle frontend or mobile."
   - *Goal*: Verify that these are correctly mapped to **Drop Zone Triggers**.
10. **The High-Volume Stress**: Provide 20+ small "Micro-Cases."
    - *Goal*: Test the Compiler Node's ability to rank and select the top 5-7 most important heuristics.

---

## 🛠️ Step-by-Step Execution Process

### Step 1: Prepare your Test Expert
Create a new directory in `data/` for your test expert:
```powershell
mkdir data/test_expert_01/knowledge_hub
mkdir data/test_expert_01/master_cases
```
Place your test `.md` or `.txt` files into these folders.

### Step 2: Trigger the Extraction
Open your terminal (or use Postman/Thunder Client) and send a POST request to start the engine:
**URL**: `http://localhost:8000/extract/start`
**Body**:
```json
{
  "expert_id": "test_expert_01",
  "expert_name": "Test Persona",
  "expert_role": "Subject Matter Expert",
  "reader_type": "filesystem"
}
```

### Step 3: Monitor Progress
Copy the `job_id` from the response and check the status:
**URL**: `http://localhost:8000/extract/{job_id}/status`
*Watch for the `current_node` to move from `ingestion` -> `journalist` -> `compiler`.*

### Step 4: Shadow Review
Once the status is `complete`, open your dashboard:
👉 [http://localhost:8000/dashboard/](http://localhost:8000/dashboard/)

1. Select your **Test Job** from the sidebar.
2. **Review Heuristics**: Does the "Decision" match what was in your documents?
3. **Review Reasoning**: Does the "Why" sound like the expert's philosophy?
4. **Tweak**: Make any corrections directly in the UI.

### Step 5: Final Approval & Export
1. Click **Approve & Publish**.
2. Run the export script to see your final AI System Prompt:
```powershell
python scripts/export_prompt.py {job_id}
```

---

## 🚩 Expected Results
- **Success**: The exported prompt contains at least 3 unique heuristics with logical "Reasoning."
- **Success**: "Drop Zones" correctly identify topics the documents didn't cover.
- **Warning**: The dashboard should show "Quality Warnings" if documents are too short or conflicting.
