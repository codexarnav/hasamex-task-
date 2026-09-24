"""Research Copilot API endpoint."""
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.copilot import CopilotRequest, CopilotResponse
from app.services.copilot_service import CopilotService

router = APIRouter(tags=["Copilot"])


@router.post("/projects/{project_id}/ask", response_model=CopilotResponse, status_code=status.HTTP_200_OK)
async def ask_copilot(
    project_id: UUID,
    payload: CopilotRequest,
    db: AsyncSession = Depends(get_db),
):
    """Ask an arbitrary qualitative inquiry across the research project.
    The Copilot synthesizes an answer grounded strictly in transcript evidence with traceable source citations.
    """
    service = CopilotService(db)
    return await service.ask(project_id=project_id, question=payload.question)
