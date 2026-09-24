"""Research analysis orchestration and synthesis endpoints."""
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, status, Body
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.answer import AnalysisResponse, AnalysisQuestionResponse
from app.services.analysis_service import AnalysisService

router = APIRouter(tags=["Analysis"])


class AnalysisRequest(BaseModel):
    """Optional request body for scoping analysis to specific transcripts."""
    transcript_ids: Optional[list[UUID]] = None


@router.post("/projects/{project_id}/analysis", response_model=AnalysisResponse, status_code=status.HTTP_200_OK)
async def run_analysis(
    project_id: UUID,
    body: Optional[AnalysisRequest] = Body(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Trigger the complete qualitative research analysis flow:
    - Utterance retrieval and LLM evidence classification
    - Grounded expert answer generation with provenance validation
    - Cross-expert difference detection
    - Strategic project insight synthesis

    Optionally pass transcript_ids to scope analysis to specific transcripts.
    """
    service = AnalysisService(db)
    transcript_ids = body.transcript_ids if body else None
    return await service.run_full_analysis(project_id, transcript_ids=transcript_ids)


@router.get("/projects/{project_id}/analysis", response_model=AnalysisResponse)
async def get_analysis(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get the current analysis answers and grounded evidence for all project questions."""
    service = AnalysisService(db)
    return await service.get_project_analysis(project_id)


@router.get("/projects/{project_id}/analysis/{question_id}", response_model=AnalysisQuestionResponse)
async def get_question_analysis(
    project_id: UUID,
    question_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get analysis answers and supporting evidence for a single research question."""
    service = AnalysisService(db)
    return await service.get_question_analysis(project_id, question_id)
