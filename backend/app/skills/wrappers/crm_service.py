from app.skills.wrappers.resilience import with_retry, TransientNetworkError, ExternalAPIException
from app.skills.wrappers.base_wrapper import BaseSkillWrapper
from typing import Dict, Any

class CRMServiceWrapper(BaseSkillWrapper):
    SKILL_NAMES = ["write_to_crm"]

    @staticmethod
    def execute(skill_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return CRMServiceWrapper.write_to_crm(payload)

    @staticmethod
    def describe_result(skill_name: str, result: Dict[str, Any]) -> str:
        return "CRM record has been saved successfully."

    @staticmethod
    @with_retry()
    def write_to_crm(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generic wrapper for CRM interactions.
        """
        headers = {"Authorization": "Bearer MOCK_CRM_TOKEN"}
        
        print(f"Calling External CRM API...")
        
        if payload.get("trigger_error"):
            raise TransientNetworkError("CRM Database locked.")
            
        return {"provider_status": "saved", "crm_record_id": "rec_555"}
