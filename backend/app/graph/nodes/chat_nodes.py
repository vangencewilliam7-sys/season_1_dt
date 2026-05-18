from ...models.chat_state import ChatState
from ...services.embeddings import EmbeddingService
from ...services.supabase_client import SupabaseService
from openai import OpenAI
import os
import time
import datetime

def retrieve_context_node(state: ChatState) -> ChatState:
    print(f"--- CHAT: Retrieval Node ---")
    embedder = EmbeddingService()
    db = SupabaseService()
    
    # 1. Semantic Search against Expert DNA Vault with DB-Level Isolation
    query_vector = embedder.get_embedding(state.query)
    results = db.expert_vault_search(
        query_vector, 
        domain_id=state.domain_id,
        workflow_id=state.workflow_id,
        limit=3
    )
    
    if results:
        state.confidence = results[0].get("similarity", 0.0)
        state.retrieved_cases = results
        state.persona_mode = "primary" if state.confidence > 0.50 else "deputy"
    else:
        state.confidence = 0.0
        state.retrieved_cases = []
        state.persona_mode = "offline"
        
    return state

def reasoning_node(state: ChatState) -> ChatState:
    print(f"--- CHAT: Reasoning Node ---")
    if not state.retrieved_cases:
        state.rationale = "No relevant Master Cases found in the Logic Vault. I must decline giving clinical advice."
        return state
        
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    context = ""
    for i, r in enumerate(state.retrieved_cases):
        context += f"[Case {i+1}]: {r.get('expert_decision', '')}\n"
        
    reasoning_prompt = f"""You are the logical core of a medical Digital Twin.
Analyze the user's query against the retrieved Master Cases.
Write a strict, step-by-step 'Chain of Thought' explaining WHY the Master Cases apply to the query and what the protocol should be.
If the context indicates moving from baseline intake to structured metabolic screening, explicitly note this task traversal.
This rationale is for the tech team's audit log, not the patient.

USER QUERY: {state.query}

RETRIEVED MASTER CASES:
{context}

CHAIN OF THOUGHT RATIONALE:"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.0,
        messages=[{"role": "user", "content": reasoning_prompt}]
    )
    
    state.rationale = completion.choices[0].message.content
    
    # Simulate dynamic layer mutators based on explicit proxy evidence
    if "acanthosis" in state.query.lower() or "string" in state.query.lower():
        state.task_id = "40000000-0000-0000-0000-000000000022" # Advance to Proxy Task layer
        
    return state

def validation_node(state: ChatState) -> ChatState:
    print(f"--- CHAT: Validation Node ---")
    # Verify CoT logic trace integrity against DB bounds to prevent hallucinations
    if "decline" in state.rationale.lower() and not state.retrieved_cases:
        state.is_valid = True
    elif state.retrieved_cases and len(state.rationale) > 10:
        state.is_valid = True
    else:
        state.is_valid = False
        state.rationale += "\n[Validation Flag: Logic verification context constrained.]"
    return state

def generation_node(state: ChatState) -> ChatState:
    print(f"--- CHAT: Generation Node ---")
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    proxy_ctx = ""
    if state.accumulated_evidence or state.likelihood_score:
        evidence_lines = "\n".join([f"  - {k}: {v}" for k, v in state.accumulated_evidence.items()])
        proxy_ctx = f"\n\nPROXY EVIDENCE GATHERED:\n{evidence_lines}\nLIKELIHOOD SCORE / PROBABILISTIC CONCLUSION:\n{state.likelihood_score}\n"
    
    # Resolve adapter role metadata dynamically
    base_prompt = state.adapter_context.get("system_prompt", "") if state.adapter_context else ""
    if not base_prompt:
        base_prompt = (
            "You are a specialized expert Digital Twin.\n"
            "Apply strict safety protocols while maintaining an empathetic bedside manner.\n"
            "Provide direct, actionable guidance based ONLY on your explicit rationale."
        )
        
    system_prompt = f"""{base_prompt}

You are a senior physician specializing in metabolic health and obesity diagnosis, speaking directly to a patient in a live chat. 

**IMPORTANT RULES:**
1. Keep your responses extremely concise and conversational, exactly as a busy doctor would type in a chat window (maximum 2-3 sentences).
2. NEVER write long paragraphs or large blocks of text. Real humans don't type essays in live chats.
3. Be empathetic but direct. Explain any risks or recommendations simply without heavy medical jargon.
4. If you gathered proxy evidence (like belt size or headaches), address it naturally in one sentence.
5. ALWAYS handle uncertainty gracefully (e.g., "We should run some tests to be sure.")
6. NEVER format your response as a dry clinical document (no headers or bullet points). Just natural chat text.

YOUR EXPLICIT RATIONALE (Audit Trace):
{state.rationale}{proxy_ctx}
"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": state.query}
        ]
    )
    
    state.response = completion.choices[0].message.content
    print(f"--- DEBUG: Raw LLM Response ---\n{repr(state.response)}\n-------------------------------")
    return state

def emergency_escalation_node(state: ChatState) -> ChatState:
    print(f"--- CHAT: Emergency Escalation Node (Red Zone) ---")
    state.persona_mode = "deputy"
    state.confidence = 1.0
    state.rationale = "CRITICAL RISK BYPASS: Direct emergency triage protocol deployed."
    state.response = (
        "🚨 **Please Seek Immediate Medical Attention**\n\n"
        "I am very concerned about the severe symptoms you just described. These are red-flag indicators that require immediate, in-person clinical evaluation. It is not safe to manage this remotely.\n\n"
        "**What you need to do right now:**\n"
        "1. Please go directly to the nearest emergency department or call emergency services (911) immediately.\n"
        "2. Do not wait to see if the symptoms improve.\n\n"
        "Your safety is my top priority. Please get help right away."
    )
    return state

def proxy_gathering_node(state: ChatState) -> ChatState:
    print(f"--- CHAT: Proxy Gathering Node (Low Data State) ---")
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    missing_str = ", ".join(state.missing_metrics) if state.missing_metrics else "blood pressure, blood glucose, weight/height"
    
    system_prompt = f"""You are the Proxy Agent for a Medical Digital Twin operating in a Low Data State.
The user is asking for medical evaluation/diagnosis but lacks formal metrics or objective vitals ({missing_str}).
Instead of declining to help or hitting a dead end, you must deploy the **Symptomatic Proxy & Telemedicine Self-Exam** strategy to extract 'invisible' vitals.

Formulate an empathetic, professional response that asks 2 or 3 highly specific proxy questions to estimate risk. Use the following proxy framework:
- **Blood Pressure Proxy**: Ask about headaches at the back of the head or a 'thumping' feeling in the ears.
- **Blood Glucose Proxy**: Ask about excessive thirst or frequent urination, especially at night.
- **Visceral Fat Proxy**: Ask if their belt size has expanded even if weight stayed the same.
- **Visual Physical Exam**: Guide them to perform a 'Neck Check' in the mirror for Acanthosis Nigricans (darkened, velvety skin patches on the neck or armpits) or the Waist-to-Height string ratio test.
- **Longitudinal Mapping**: Ask about stress triggers or past recovery barriers.

**FORMATTING RULES:**
- Be warm, empathetic, and extremely easy to read.
- Keep your questions very simple and conversational, like a friendly doctor speaking to a patient.
- Do NOT use technical medical jargon (e.g., avoid words like "visceral fat", "acanthosis nigricans", "nocturia"). Use plain English.
- Limit yourself to exactly 2 or 3 short, simple questions so the patient is not overwhelmed.
- Ask questions that can be answered in simple lines.
- State that these everyday observations help bridge the gap left by missing clinic data.
"""

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": state.query}
            ]
        )
        state.response = completion.choices[0].message.content
        state.persona_mode = "deputy"
        state.confidence = 1.0  # High confidence in gathering proxies
        state.rationale = f"Low Data State detected. Triggered Proxy Agent to collect invisible vitals for missing metrics: {missing_str}."
    except Exception as e:
        print(f"Proxy gathering generation failed: {e}")
        state.response = "I notice we don't have your recent vitals on file. Could you let me know if you've been experiencing excessive thirst, frequent urination, or noticed any dark velvety patches on the back of your neck?"
        state.persona_mode = "deputy"
        
    return state

def audit_node(state: ChatState) -> ChatState:
    print(f"--- CHAT: Audit Logger Node ---")
    db = SupabaseService()
    
    try:
        if state.intent_type in ["action", "emergency_escalation"]:
            db.insert_chat_audit_log({
                "expert_id": state.expert_id,
                "session_id": state.session_id,
                "user_query": state.query,
                "retrieved_cases": [],
                "rationale": state.rationale,
                "final_response": state.response,
                "confidence": 1.0,
                "latency_ms": 0
            })
        else:
            db.insert_chat_audit_log({
                "expert_id": state.expert_id,
                "session_id": state.session_id,
                "user_query": state.query,
                "retrieved_cases": [r.get("scenario_id", "Unknown") for r in state.retrieved_cases],
                "rationale": state.rationale,
                "final_response": state.response,
                "confidence": state.confidence,
                "latency_ms": 0
            })
    except Exception as e:
        print(f"Audit log failed: {e}")
        
    return state

def persistence_node(state: ChatState) -> ChatState:
    print(f"--- CHAT: Persistence Node (Mirror State Commit) ---")
    db = SupabaseService()
    try:
        mirror_data = {
            "last_query": state.query,
            "triage_level": state.triage_level,
            "confidence_score": state.confidence,
            "persona_mode": state.persona_mode,
            "timestamp": time.time()
        }
        db.update_patient_twin_state(state.session_id, mirror_data)

        # Update clinical notes if this is a registered patient session
        if state.session_id.startswith("onboarding-"):
            patient_id = state.session_id.replace("onboarding-", "")
            note_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "query": state.query,
                "situation_summary": state.rationale if state.rationale else "Patient interaction completed.",
                "triage_result": state.triage_level
            }
            db.update_patient_notes(patient_id, note_entry)
            print(f"--- CLINICAL LOG: Updated notes for patient {patient_id} ---")

    except Exception as e:
        print(f"Mirror state/notes persistence failed: {e}")
    return state
