"""Project service for managing project lifecycle."""
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectListResponse
from app.core.exceptions import ProjectNotFoundError
from app.core.enums import ProjectStatus
from app.core.logging import get_logger

logger = get_logger("services.project")


class ProjectService:
    """Service handling project management operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_project(self, data: ProjectCreate) -> Project:
        """Create a new research project."""
        project = Project(
            name=data.name,
            objective=data.objective,
            status=ProjectStatus.PENDING.value,
        )
        self.db.add(project)
        await self.db.flush()
        await self.db.refresh(project)
        logger.info(f"Project created: {project.id}", extra={"operation": "create_project", "project_id": str(project.id)})
        return project

    async def get_project(self, project_id: UUID) -> Project:
        """Get project by ID."""
        stmt = select(Project).where(Project.id == project_id)
        result = await self.db.execute(stmt)
        project = result.scalar_one_or_none()
        if not project:
            raise ProjectNotFoundError(project_id)
        return project

    async def list_projects(self, skip: int = 0, limit: int = 50) -> tuple[list[Project], int]:
        """List all projects with pagination."""
        total_stmt = select(func.count(Project.id))
        total_res = await self.db.execute(total_stmt)
        total = total_res.scalar() or 0

        stmt = select(Project).order_by(Project.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        projects = list(result.scalars().all())
        return projects, total

    async def update_status(self, project_id: UUID, status: ProjectStatus) -> Project:
        """Update project processing status."""
        project = await self.get_project(project_id)
        project.status = status.value
        await self.db.flush()
        return project
