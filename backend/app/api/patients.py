from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from ..services.supabase_client import SupabaseService

router = APIRouter()

class PatientRegistration(BaseModel):
    full_name: str
    email: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    height_cm: float
    weight_kg: float

@router.post("/register")
async def register_patient(reg: PatientRegistration):
    db = SupabaseService()
    
    # Calculate BMI
    height_m = reg.height_cm / 100
    bmi = reg.weight_kg / (height_m * height_m)
    
    patient_data = {
        "full_name": reg.full_name,
        "email": reg.email,
        "dob": reg.dob.isoformat() if reg.dob else None,
        "gender": reg.gender,
        "height_cm": reg.height_cm,
        "weight_kg": reg.weight_kg,
        "base_bmi": round(bmi, 2)
    }
    
    try:
        result = db.create_patient(patient_data)
        if not result or not result.data:
            raise HTTPException(status_code=500, detail="Failed to create patient record")
            
        patient = result.data[0]
        
        # Initialize the Digital Twin state for this patient
        session_id = f"onboarding-{patient['id']}"
        mirror_state = {
            "patient_name": patient["full_name"],
            "vitals": {
                "bmi": patient["base_bmi"],
                "height": patient["height_cm"],
                "weight": patient["weight_kg"]
            },
            "triage_level": "GREEN_ZONE",
            "onboarding_complete": True
        }
        
        db.update_patient_twin_state(session_id, mirror_state)
        
        return {
            "status": "success",
            "patient_id": patient["id"],
            "session_id": session_id,
            "base_bmi": patient["base_bmi"],
            "message": "Patient registered and Digital Twin initialized."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
