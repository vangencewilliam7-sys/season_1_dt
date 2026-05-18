from app.skills.wrappers.resilience import with_retry, TransientNetworkError, ExternalAPIException
from app.skills.wrappers.base_wrapper import BaseSkillWrapper
from typing import Dict, Any

class CalendarServiceWrapper(BaseSkillWrapper):
    SKILL_NAMES = ["book_appointment"]

    @staticmethod
    def execute(skill_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return CalendarServiceWrapper.book_appointment(payload)

    @staticmethod
    def describe_result(skill_name: str, result: Dict[str, Any]) -> str:
        return "Your appointment has been booked successfully."

    @staticmethod
    @with_retry()
    def book_appointment(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Wrapper for booking appointments via an external calendar API.
        """
        headers = {"Authorization": "Bearer MOCK_CALENDAR_TOKEN"}
        
        print(f"Calling External Calendar API for patient {payload.get('patient_id')}...")
        
        # Simulated failure for testing the retry mechanism
        # If patient_id starts with '0000', trigger timeout
        if str(payload.get("patient_id")).startswith("00000000"):
            print("Calendar API Timeout!")
            raise TransientNetworkError("Calendar API timed out.")
            
        return {"provider_status": "booked", "calendar_event_id": "evt_12345"}
