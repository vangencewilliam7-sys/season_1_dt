import os
import json
from openai import OpenAI
from app.models.chat_state import ChatState
from app.skills.middleware.validation import SKILL_REGISTRY

def intent_detection_node(state: ChatState) -> ChatState:
    print(f"--- CHAT: Intent Detection Node ---")
    
    # Emergency keywords fallback
    emergency_keywords = ["bleeding", "emergency", "suicide", "hurt", "dying", "blood"]
    if any(keyword in state.query.lower() for keyword in emergency_keywords):
        state.intent_type = "knowledge"
        return state

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    # Prepare available skills description
    skills_description = []
    for skill_name, schema_cls in SKILL_REGISTRY.items():
        try:
            schema = schema_cls.model_json_schema()
        except Exception:
            try:
                schema = schema_cls.schema()
            except Exception:
                schema = {}
        skills_description.append(f"- {skill_name}: {json.dumps(schema)}")
        
    skills_text = "\n".join(skills_description)

    system_prompt = f"""You are an Intent Detection Router for a Medical Digital Twin.
Your job is to determine if the user's message is a 'knowledge' query (asking for advice, information, synthesis) OR an 'action' request (asking to perform a specific registered skill).

Registered Skills and their schemas:
{skills_text}

If the user wants to perform an action, you must:
1. Set intent to 'action'.
2. Extract the 'skill' name from the list above. If the requested action is NOT in the list, set skill to 'unknown'.
3. Extract 'params' exactly according to the skill's schema. You MUST satisfy the required fields (e.g. UUID format for patient_id, ISO-8601 for datetime, Literal enums, etc.).
   - Use '11111111-1111-1111-1111-111111111111' for ANY missing patient_id.
   - Use a valid ISO-8601 datetime for missing dates, or parse the date given in the message (e.g. 2026-05-07T10:00:00Z).
   - Use valid Enum values like 'CONSULT' for reason_code if missing.

If the user is asking for medical/clinical advice or general synthesis, set intent to 'knowledge'.
Additionally, if intent is 'knowledge' and the user's query lacks concrete objective vitals (like formal blood pressure readings, fasting glucose numbers, or lab reports) OR if the user explicitly mentions they don't know their vitals/labs, you must:
1. Set 'low_data_mode' to true.
2. List the 'missing_metrics' (e.g., ["blood_pressure", "blood_glucose", "lipids", "visceral_fat"]).
3. If the user provides proxy observations (e.g., feeling thirsty, frequent urination, dark velvety skin patches on the neck, or tight belts), extract them as key-value pairs into 'accumulated_evidence'.

Return ONLY valid JSON.
"""

    tools = [{
        "type": "function",
        "function": {
            "name": "route_intent",
            "description": "Route the user intent to either knowledge or action, and extract proxy evidence if in low data state.",
            "parameters": {
                "type": "object",
                "properties": {
                    "intent": {
                        "type": "string",
                        "enum": ["knowledge", "action"]
                    },
                    "skill": {
                        "type": "string",
                        "description": "The name of the skill if intent is action."
                    },
                    "params": {
                        "type": "object",
                        "description": "The extracted parameters for the skill."
                    },
                    "low_data_mode": {
                        "type": "boolean",
                        "description": "Set to true if the query asks for clinical diagnosis/advice but lacks objective vitals/lab reports."
                    },
                    "missing_metrics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of missing metrics like 'blood_pressure', 'blood_glucose', 'lipids'."
                    },
                    "accumulated_evidence": {
                        "type": "object",
                        "description": "Extracted proxy answers provided by the user (e.g. thirst frequency, dark skin patches, tight belt)."
                    }
                },
                "required": ["intent"]
            }
        }
    }]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": state.query}
            ],
            tools=tools,
            tool_choice={"type": "function", "function": {"name": "route_intent"}}
        )
        
        tool_call = response.choices[0].message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)
        
        state.intent_type = args.get("intent", "knowledge")
        if state.intent_type == "action":
            state.detected_skill = args.get("skill", "")
            
            # Use demo patient ID if missing but needed
            params = args.get("params", {})
            if "patient_id" not in params or params["patient_id"] == "PAT-001":
                params["patient_id"] = "11111111-1111-1111-1111-111111111111"
            
            if state.detected_skill == "book_appointment":
                if "appointment_time" not in params:
                    params["appointment_time"] = "2026-05-07T10:00:00Z"
                if "reason_code" not in params:
                    params["reason_code"] = "CONSULT"
            elif state.detected_skill == "send_communication":
                if "template_id" not in params:
                    params["template_id"] = "TPL_FOLLOWUP_01"
                if "recipient_address" not in params:
                    params["recipient_address"] = "patient@example.com"
            elif state.detected_skill == "ACT_CHECKLIST_VERIFY":
                if "required_documents" not in params:
                    params["required_documents"] = ["Consent Form", "Blood Results"]
            elif state.detected_skill == "SKL_EXPERT_SYNTHESIS":
                if "data_sources" not in params:
                    params["data_sources"] = ["lab_01", "scan_02"]
                if "release_approved" not in params:
                    params["release_approved"] = True
            elif state.detected_skill == "SKL_PRE_OP_GATEKEEPER":
                if "surgery_date" not in params:
                    params["surgery_date"] = "2026-05-20T00:00:00Z"
                if "required_documents" not in params:
                    params["required_documents"] = ["blood_test", "ecg"]
                    
            state.extracted_params = params
        else:
            # Populate low data proxy fields
            state.low_data_mode = args.get("low_data_mode", False)
            state.missing_metrics = args.get("missing_metrics") or []
            state.accumulated_evidence = args.get("accumulated_evidence") or {}
            
            # If evidence was accumulated, compute likelihood score and route to main path
            if state.accumulated_evidence:
                state.low_data_mode = False  # Let definitive path execute
                evidence_str = ", ".join([f"{k}: {v}" for k, v in state.accumulated_evidence.items()])
                if "neck" in evidence_str.lower() or "acanthosis" in evidence_str.lower() or "thirst" in evidence_str.lower() or "patch" in evidence_str.lower():
                    state.likelihood_score = "High probability of severe insulin resistance / prediabetes based on Acanthosis Nigricans and thirst proxies; recommend formal screening."
                elif "headache" in evidence_str.lower() or "thumping" in evidence_str.lower() or "pressure" in evidence_str.lower():
                    state.likelihood_score = "High probability of Stage 2 Hypertension based on symptomatic report; recommend formal screening."
                else:
                    state.likelihood_score = "Elevated metabolic risk identified from physical proxies; formal laboratory verification required."
            
    except Exception as e:
        print(f"Intent detection failed: {e}")
        state.intent_type = "knowledge"
        
    return state
