"""Expert management API endpoints."""
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.expert import Expert
from app.models.project import Project
from app.schemas.expert import ExpertCreate, ExpertResponse, ExpertsListResponse
from app.core.exceptions import ProjectNotFoundError

router = APIRouter(tags=["Experts"])


@router.post("/projects/{project_id}/experts", response_model=ExpertResponse, status_code=status.HTTP_201_CREATED)
async def create_expert(
    project_id: UUID,
    data: ExpertCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register an expert interviewee for a research project."""
    p_stmt = select(Project).where(Project.id == project_id)
    p_res = await db.execute(p_stmt)
    if not p_res.scalar_one_or_none():
        raise ProjectNotFoundError(project_id)

    expert = Expert(
        project_id=project_id,
        name=data.name,
        role=data.role,
        market=data.market,
        organization=data.organization,
    )
    db.add(expert)
    await db.flush()
    await db.refresh(expert)
    return expert


@router.get("/projects/{project_id}/experts", response_model=ExpertsListResponse)
async def list_experts(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """List all expert interviewees in a project."""
    stmt = select(Expert).where(Expert.project_id == project_id).order_by(Expert.created_at.asc())
    res = await db.execute(stmt)
    experts = list(res.scalars().all())
    return ExpertsListResponse(
        experts=[ExpertResponse.model_validate(e) for e in experts],
        total=len(experts),
    )
