# Implementation Plan — Phase 3 (Social Learner) Frontend

This plan focuses on making the **Knowledge Hub Dashboard** fully functional. We will transition from mock data to a real-time, audio-driven "Expert DNA" capture system.

## User Review Required

> [!IMPORTANT]
> **Browser Recording**: We will use the native **MediaRecorder API**. This requires microphone permissions from the user when they access the Knowledge Hub.
> **Binary Uploads**: Audio will be sent as a `.wav` or `.webm` blob directly to the local backend for transcription via the local Whisper model.
> **Industry Context**: The UI strings (e.g., "Medical Dosage" vs "Legal Clause") will be fetched from the `/api/context` endpoint to ensure the hub reflects the correct industry.

## Proposed Changes

### 1. Frontend: Knowledge Hub Functionality

#### [MODIFY] [KnowledgeHub.jsx](file:///c:/Users/harin/Downloads/js_dt/frontend/src/pages/KnowledgeHub.jsx)
- **Audio Capture**: Implement `MediaRecorder` logic for start/stop recording.
- **API Integration**: 
    - `useEffect` to fetch industry context and pending scenarios on load.
    - `handleSubmit` to POST audio blobs to `/api/resolve`.
- **State Flow**: Handle the response from the backend (transcript + parsed logic) and switch to the **Audit Phase** automatically.

### 2. Backend: Endpoint Hardening

#### [MODIFY] [ingest.py](file:///c:/Users/harin/Downloads/knowledge_hub/backend/app/api/ingest.py)
- Ensure `/api/resolve` correctly returns the extracted logic JSON for the UI's "Visual Audit" gate.

---

## Open Questions

### 1. Recording Format
Should I implement a visual **Audio Waveform** indicator during recording, or is a simple "Recording..." pulse sufficient for this version?

### 2. Mock Data
Would you like me to keep a set of "Demo Scenarios" in the sidebar if the database is currently empty, or should it strictly display real extracted gaps?

---

## Verification Plan

### Manual Verification
1.  Open the `/knowledge-hub` dashboard.
2.  Select a pending scenario.
3.  Click the microphone and speak for 5-10 seconds.
4.  Stop recording and click "Submit".
5.  Verify that the "Extracted Decision" and "Audit Passed" states update with the actual transcript.
