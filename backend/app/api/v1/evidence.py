"""Evidence retrieval and provenance API endpoints."""
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.evidence import EvidenceResponse, EvidenceListResponse
from app.services.evidence_service import EvidenceService

router = APIRouter(tags=["Evidence"])


@router.get("/projects/{project_id}/evidence", response_model=EvidenceListResponse)
async def list_project_evidence(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """List all validated evidence records in a project with full utterance and timestamp provenance."""
    service = EvidenceService(db)
    evidence_items = await service.list_project_evidence(project_id)
    return EvidenceListResponse(
        evidence=[service.format_evidence_response(e) for e in evidence_items],
        total=len(evidence_items),
    )


@router.get("/evidence/{evidence_id}", response_model=EvidenceResponse)
async def get_evidence(
    evidence_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get single evidence record with detailed quote, speaker, transcript, and timestamp provenance."""
    service = EvidenceService(db)
    evidence = await service.get_evidence(evidence_id)
    return service.format_evidence_response(evidence)
