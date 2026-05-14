"""
validation.py — Skill Validation Gateway (Full Auto-Discovery)
================================================================
Validates and authorizes skill execution requests.

The SKILL_REGISTRY is built by auto-scanning every .py file in
schemas/ for dicts ending in _SKILL_REGISTRY. When a developer adds
a new domain schema file (e.g., schemas/legal.py with LEGAL_SKILL_REGISTRY),
it is merged automatically — NO EDITS TO THIS FILE are ever needed.
"""
import importlib
import pathlib
from fastapi import HTTPException
from pydantic import ValidationError, BaseModel
from typing import Dict, Any, Type
from sqlalchemy.orm import Session

from app.skills.schemas.base import SkillRequest
from app.skills.database.models import SkillDefinition


# ── Auto-Discovery: Scan schemas/*.py for *_SKILL_REGISTRY dicts ──────────────

def _discover_skill_registries() -> Dict[str, Type[BaseModel]]:
    """
    Scan every .py file in the schemas/ package. For each file, find any
    module-level dict whose name ends with '_SKILL_REGISTRY' and merge
    its contents into the unified registry.

    Convention: each domain schema file exports exactly one registry dict.
        - schemas/healthcare.py  → HEALTHCARE_SKILL_REGISTRY
        - schemas/it.py          → IT_SKILL_REGISTRY
        - schemas/presales.py    → PRESALES_SKILL_REGISTRY
        etc.
    """
    merged: Dict[str, Type[BaseModel]] = {}
    schemas_dir = pathlib.Path(__file__).parent.parent / "schemas"

    skip_files = {"__init__.py", "base.py", "contracts.py"}

    for py_file in sorted(schemas_dir.glob("*.py")):
        if py_file.name in skip_files:
            continue

        module = importlib.import_module(f"app.skills.schemas.{py_file.stem}")

        for attr_name in dir(module):
            if attr_name.endswith("_SKILL_REGISTRY"):
                registry = getattr(module, attr_name)
                if isinstance(registry, dict):
                    merged.update(registry)

    return merged


SKILL_REGISTRY: Dict[str, Type[BaseModel]] = _discover_skill_registries()


class ValidationGateway:
    @staticmethod
    def authorize_request(db: Session, request: SkillRequest) -> None:
        """
        Checks the database to ensure the skill is active and
        the expert is authorized to run it (mocked expert logic).
        """
        skill_def = db.query(SkillDefinition).filter(SkillDefinition.skill_name == request.skill_name).first()
        if skill_def and not skill_def.is_active:
            raise HTTPException(
                status_code=403,
                detail=f"Skill '{request.skill_name}' is currently disabled by the administrator."
            )
        # Note: further expert-specific permission checks could be added here.

    @staticmethod
    def validate_request(request: SkillRequest) -> BaseModel:
        """
        Intercepts the SkillRequest, looks up the corresponding schema,
        and validates the payload.
        """
        skill_name = request.skill_name
        payload_schema = SKILL_REGISTRY.get(skill_name)

        if not payload_schema:
            raise HTTPException(
                status_code=400,
                detail=f"Skill '{skill_name}' is not recognized in the registry."
            )

        try:
            # Validate the nested payload dictionary against the specific schema
            validated_payload = payload_schema(**request.payload)
            return validated_payload
        except ValidationError as e:
            # Reformat the Pydantic error into a structured response for the LLM
            error_details = e.errors()
            missing_fields = []
            invalid_fields = []

            for err in error_details:
                field = err["loc"][0] if err["loc"] else "unknown"
                if err["type"] == "missing":
                    missing_fields.append(field)
                else:
                    invalid_fields.append({"field": field, "error": err["msg"]})

            raise HTTPException(
                status_code=422,
                detail={
                    "message": "Payload Validation Failed",
                    "missing_fields": missing_fields,
                    "invalid_fields": invalid_fields,
                    "correction_instructions": "Please correct the payload according to the strict schema."
                }
            )
