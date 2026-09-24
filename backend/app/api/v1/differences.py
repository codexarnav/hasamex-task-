"""Cross-expert difference API endpoints."""
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.difference import DifferencesListResponse
from app.services.difference_service import DifferenceService

router = APIRouter(tags=["Differences"])


@router.get("/projects/{project_id}/differences", response_model=DifferencesListResponse)
async def list_differences(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """List cross-expert differences, divergences, and unique perspectives for a project."""
    service = DifferenceService(db)
    differences = await service.list_differences(project_id)
    return DifferencesListResponse(
        differences=[service.format_difference_response(d) for d in differences],
        total=len(differences),
    )
