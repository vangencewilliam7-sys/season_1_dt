from app.skills.wrappers.resilience import with_retry, TransientNetworkError, ExternalAPIException
from app.skills.wrappers.base_wrapper import BaseSkillWrapper
from typing import Dict, Any

class EmailServiceWrapper(BaseSkillWrapper):
    SKILL_NAMES = ["send_communication"]

    @staticmethod
    def execute(skill_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return EmailServiceWrapper.send_communication(payload)

    @staticmethod
    def describe_result(skill_name: str, result: Dict[str, Any]) -> str:
        return "The communication has been sent successfully."

    @staticmethod
    @with_retry()
    def send_communication(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Wrapper for sending emails via an external provider (e.g., SendGrid).
        """
        # 1. Inject Auth Headers (Simulated)
        headers = {"Authorization": "Bearer MOCK_EMAIL_TOKEN"}
        
        # 2. Simulate External API Call
        print(f"Calling External Email API with template: {payload.get('template_id')}...")
        
        # Simulated failure for testing the retry mechanism
        if payload.get("dynamic_vars", {}).get("trigger_transient_error"):
            print("Email API returned 503 Service Unavailable!")
            raise TransientNetworkError("Email API is temporarily down.")
            
        if payload.get("dynamic_vars", {}).get("trigger_fatal_error"):
            print("Email API returned 401 Unauthorized!")
            raise ExternalAPIException("Invalid API Key for Email Service.")
            
        return {"provider_status": "sent", "external_id": "msg_987654321"}
