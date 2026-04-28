# Implementation Plan — Local-First & Industry Agnostic Refactor

This plan refactors the existing Knowledge Hub architecture to meet the new constraints: standalone operation, local SLM/STT models, and cross-industry modularity.

## User Review Required

> [!IMPORTANT]
> **SLM Choice**: We are switching to **Phi-3** for the SLM Auditor and Echo Verification nodes. This significantly reduces costs and allows for 100% private clinical logic extraction.
> **STT Choice**: We are switching to **faster-whisper** (Open Source) for local audio transcription.
> **Industry Agnostic**: I will implement a "Contextual Jacketing" system. Industry-specific rules (Fertility, Legal, Finance) will be injected as "Context Packs" rather than being hardcoded in the graph nodes.

## Proposed Changes

### 1. Model Services (Refactor)

#### [MODIFY] [slm_auditor.py](file:///c:/Users/harin/Downloads/knowledge_hub/backend/app/services/slm_auditor.py)
- Remove OpenAI client dependency.
- Integrate with **Phi-3** (via Ollama or local API).
- Standardize prompt templates for cross-industry auditing.

#### [MODIFY] [stt.py](file:///c:/Users/harin/Downloads/knowledge_hub/backend/app/services/stt.py)
- Remove OpenAI Whisper API dependency.
- Integrate **faster-whisper** library for local CPU/GPU inference.

#### [NEW] [context_manager.py](file:///c:/Users/harin/Downloads/knowledge_hub/backend/app/services/context_manager.py)
- A new service to manage "Context Packs".
- Loads industry-specific metadata (e.g., "Fertility" vs "Real Estate") to guide the Divergence Engine and Scenario Generator.

### 2. Implementation & Routing

#### [MODIFY] [.env](file:///c:/Users/harin/Downloads/knowledge_hub/backend/.env)
- Add `OLLAMA_BASE_URL` (optional, for Phi-3).
- Add `WHISPER_MODEL_SIZE` (tiny, base, small).
- Mark `OPENAI_API_KEY` as optional (reserved for high-reasoning Generation if desired).

#### [MODIFY] [ingest.py](file:///c:/Users/harin/Downloads/knowledge_hub/backend/app/api/ingest.py)
- Ensure the pipeline can be triggered without `js_dt` session state.

---

## Open Questions

### 1. Phi-3 Infrastructure
Are you planning to run Phi-3 via **Ollama**? It is the most robust way to provide a local API for the backend to consume. If not, please specify the inference server (e.g., vLLM, llama.cpp).

### 2. Scenario Generation
For **Phase 2 (Generation)**, which requires high reasoning to build complex clinical scenarios, would you like to keep using **GPT-4o** for the "Brain" and Phi-3 only for the "Auditor", or should we attempt to move the Generator to a local model (like Llama-3-8B) as well?

### 3. Hardware for Whisper
Do you have an **NVIDIA GPU (CUDA)** available for the local Whisper service, or should I optimize the implementation for **CPU execution**?

---

## Verification Plan

### Automated Tests
- `backend/tests/test_local_slm.py`: Verify connectivity with the Phi-3 endpoint.
- `backend/tests/test_local_stt.py`: Verify that a sample audio file is transcribed locally without external API calls.

### Manual Verification
1. Run the `ingest` pipeline.
2. Confirm the "SLM Filter" is hitting the local Phi-3 instance.
3. Record a response in the UI and confirm local transcription via the terminal logs.
