"""
contracts.py — Backward-Compatible Re-Export Hub
==================================================
DEPRECATED: Do not add new schemas here.
Instead, add them to the domain-specific file:
    - schemas/healthcare.py
    - schemas/it.py
    - schemas/education.py

This file re-exports all payload classes so that existing imports
(e.g., `from app.skills.schemas.contracts import BookAppointmentPayload`)
continue to work without modification.
"""

# Healthcare payloads
from app.skills.schemas.healthcare import (
    BookAppointmentPayload,
    ActVisionOcrPayload,
    KnwReportSynthesisPayload,
    ActChecklistVerifyPayload,
    SklPreOpGatekeeperPayload,
    SklExpertSynthesisPayload,
    SklBaselineVigilancePayload,
)

# IT payloads
from app.skills.schemas.it import (
    SendCommunicationPayload,
)

# Education payloads — add re-exports here as Dev C creates them
# from app.skills.schemas.education import (...)
