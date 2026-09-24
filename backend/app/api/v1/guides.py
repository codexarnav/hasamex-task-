"""Interview guide and research question endpoints."""
from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.question import QuestionResponse, QuestionsListResponse
from app.schemas.guide import GuideResponse
from app.services.guide_service import GuideService

router = APIRouter(tags=["Interview Guide"])


@router.post("/projects/{project_id}/guide", response_model=QuestionsListResponse, status_code=status.HTTP_201_CREATED)
async def upload_guide(
    project_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload an interview guide, parse it, and dynamically extract research questions using Gemini."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    service = GuideService(db)
    guide, questions = await service.process_guide(
        project_id=project_id,
        filename=file.filename,
        content=content,
    )
    return QuestionsListResponse(
        questions=[QuestionResponse.model_validate(q) for q in questions],
        total=len(questions),
    )


@router.get("/projects/{project_id}/questions", response_model=QuestionsListResponse)
async def get_project_questions(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get all dynamically extracted research questions for a project."""
    service = GuideService(db)
    questions = await service.get_questions(project_id)
    return QuestionsListResponse(
        questions=[QuestionResponse.model_validate(q) for q in questions],
        total=len(questions),
    )
