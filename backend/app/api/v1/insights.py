"""Strategic research insight API endpoints."""
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.insight import InsightsListResponse
from app.services.insight_service import InsightService

router = APIRouter(tags=["Insights"])


@router.get("/projects/{project_id}/insights", response_model=InsightsListResponse)
async def list_insights(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """List synthesized high-level research insights for a project with supporting evidence."""
    service = InsightService(db)
    insights = await service.list_insights(project_id)
    return InsightsListResponse(
        insights=[service.format_insight_response(i) for i in insights],
        total=len(insights),
    )
