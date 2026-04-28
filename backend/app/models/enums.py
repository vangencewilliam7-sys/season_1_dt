from enum import Enum

class ImpactArchetype(str, Enum):
    SAFETY = "Safety"
    STRUCTURAL = "Structural"
    INFORMATIONAL = "Informational"

class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    EMERGENCY = "Emergency"

class AuditStatus(str, Enum):
    PASS = "Pass"
    CONFLICT = "Conflict"
    FAIL = "Fail"
