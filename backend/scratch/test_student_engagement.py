import sys
import os

# Add the backend root to sys.path so we can import 'app'
backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_root)

from app.skills.functional.skill_router import execute_skill
import uuid

def run_test():
    student_id = str(uuid.uuid4())
    
    print("===========================================")
    print("TEST 1: Query Resolution (FAST_LEARNER)")
    print("===========================================")
    payload_1 = {
        "student_id": student_id,
        "persona": "FAST_LEARNER",
        "interaction_type": "QUERY_RESOLUTION",
        "query_text": "I'm confused about how React Context API differs from Redux. Which one is faster?",
    }
    try:
        res1 = execute_skill("SKL_STUDENT_ENGAGEMENT", payload_1)
        print("Tutor Response:\n", res1["tutor_response"])
        print("\nRequires Escalation:", res1["requires_human_escalation"])
    except Exception as e:
        print(f"Failed: {e}")

    print("\n===========================================")
    print("TEST 2: Deadline Nudge (LOW_CONFIDENCE)")
    print("===========================================")
    payload_2 = {
        "student_id": student_id,
        "persona": "LOW_CONFIDENCE",
        "interaction_type": "DEADLINE_NUDGE",
        "context_data": {
            "assignment_name": "Capstone Project Proposal"
        }
    }
    try:
        res2 = execute_skill("SKL_STUDENT_ENGAGEMENT", payload_2)
        print("Tutor Response:\n", res2["tutor_response"])
        print("\nRequires Escalation:", res2["requires_human_escalation"])
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    run_test()
