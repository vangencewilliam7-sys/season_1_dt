"""
runtime/api/shadow.py

Shadow Mode API — expert review and approval of extracted Manifests.

GET  /shadow/pending            — List all manifests awaiting expert review
GET  /shadow/{job_id}/review    — Get manifest + reviewer notes for a job
POST /shadow/{job_id}/approve   — Approve manifest (marks shadow_approved = True)
POST /shadow/{job_id}/reject    — Reject manifest with correction notes (triggers re-extraction)
"""

import json
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/shadow", tags=["Shadow Mode"])


# ── Request / Response models ─────────────────────────────────────────────────

class ApprovalRequest(BaseModel):
    approved_by: str                             # Reviewer name/ID
    notes: Optional[str] = None                  # Optional notes from the expert
    modified_manifest: Optional[dict] = None     # Optional direct edits from the dashboard


class RejectionRequest(BaseModel):
    rejected_by: str
    corrections: list[dict]                      # [{"field": str, "correction": str}]
    notes: Optional[str] = None


class ShadowReviewItem(BaseModel):
    job_id: str
    expert_id: str
    status: str                                  # "pending_review" | "approved" | "rejected"
    compilation_issues: list[str]
    approved_by: Optional[str] = None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/pending", response_model=list[ShadowReviewItem])
async def list_pending_reviews():
    """
    Return all extraction jobs with completed manifests awaiting expert review.
    """
    from runtime.api.extraction import get_all_jobs
    jobs = get_all_jobs()

    pending = [
        ShadowReviewItem(
            job_id=job_id,
            expert_id=job["expert_id"],
            status="pending_review",
            compilation_issues=job.get("compilation_issues", []),
        )
        for job_id, job in jobs.items()
        if job["status"] == "complete" and job.get("final_manifest")
        and not _is_approved(job)
    ]

    logger.info(f"[ShadowAPI] {len(pending)} manifests pending review")
    return pending


@router.get("/{job_id}/review")
async def get_review_package(job_id: str):
    """
    Return the full manifest and any compilation issues for the expert to review.
    """
    from runtime.api.extraction import get_all_jobs
    jobs = get_all_jobs()

    job = jobs.get(job_id)
    if not job or job["status"] != "complete":
        raise HTTPException(status_code=404, detail=f"No completed manifest for job: {job_id}")

    return {
        "job_id": job_id,
        "expert_id": job["expert_id"],
        "manifest": json.loads(job["final_manifest"]),
        "compilation_issues": job.get("compilation_issues", []),
        "reviewer_guidance": (
            "Review each heuristic for accuracy. "
            "Check that drop_zone_triggers reflect your actual knowledge boundaries. "
            "Correct any fields that don't accurately represent your expertise."
        ),
    }


@router.post("/{job_id}/approve")
async def approve_manifest(job_id: str, request: ApprovalRequest):
    """
    Expert approves the extracted manifest.
    Sets shadow_approved = True — manifest is now production-ready.
    """
    from runtime.api.extraction import get_all_jobs
    jobs = get_all_jobs()
    from datetime import datetime

    job = jobs.get(job_id)
    if not job or job["status"] != "complete":
        raise HTTPException(status_code=404, detail=f"No completed manifest for job: {job_id}")

    # Update the manifest with approval metadata
    if request.modified_manifest:
        manifest = request.modified_manifest
    else:
        manifest = json.loads(job["final_manifest"])

    manifest["shadow_approved"] = True
    manifest["approved_by"] = request.approved_by
    manifest["approved_at"] = datetime.now(__import__("datetime").UTC).isoformat()
    manifest["manifest_version"] = manifest.get("manifest_version", 1) + 1

    if request.notes:
        manifest["reviewer_notes"] = request.notes

    job["final_manifest"] = json.dumps(manifest, indent=2)
    job["shadow_status"] = "approved"

    from runtime.api.extraction import _save_jobs
    _save_jobs(jobs)

    logger.info(f"[ShadowAPI] Job {job_id} manifest approved by: {request.approved_by}")

    return {
        "status": "approved",
        "job_id": job_id,
        "manifest_version": manifest["manifest_version"],
        "message": "Manifest is now production-ready."
    }


@router.post("/{job_id}/reject")
async def reject_manifest(job_id: str, request: RejectionRequest):
    """
    Expert rejects the manifest with correction notes.
    In production, this would trigger a targeted re-extraction.
    """
    from runtime.api.extraction import get_all_jobs
    jobs = get_all_jobs()

    job = jobs.get(job_id)
    if not job or job["status"] != "complete":
        raise HTTPException(status_code=404, detail=f"No completed manifest for job: {job_id}")

    job["shadow_status"] = "rejected"
    job["rejection"] = {
        "rejected_by": request.rejected_by,
        "corrections": request.corrections,
        "notes": request.notes,
    }

    logger.info(f"[ShadowAPI] Job {job_id} rejected by: {request.rejected_by} "
                f"with {len(request.corrections)} corrections")

    from runtime.api.extraction import _save_jobs
    _save_jobs(jobs)

    return {
        "status": "rejected",
        "job_id": job_id,
        "corrections_logged": len(request.corrections),
        "message": "Corrections recorded. Re-extraction can be triggered via POST /extract/start."
    }


# ── Helper ────────────────────────────────────────────────────────────────────

def _is_approved(job: dict) -> bool:
    """Check if a job's manifest has been approved."""
    if not job.get("final_manifest"):
        return False
    try:
        manifest = json.loads(job["final_manifest"])
        return manifest.get("shadow_approved", False)
    except Exception:
        return False
