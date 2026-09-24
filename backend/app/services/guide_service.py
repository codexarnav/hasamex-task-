"""Interview guide processing and question extraction service."""
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models.guide import InterviewGuide
from app.models.question import ResearchQuestion
from app.models.project import Project
from app.schemas.guide import GuideResponse
from app.storage.local import local_storage
from app.parsers.guide_parser import extract_guide_text
from app.ai.gemini import get_gemini_client
from app.ai.prompts.guide_extraction import (
    GUIDE_EXTRACTION_SYSTEM_PROMPT,
    GUIDE_EXTRACTION_USER_PROMPT,
)
from app.ai.schemas.guide import GuideExtractionResult
from app.core.enums import GuideStatus
from app.core.exceptions import ProjectNotFoundError, GuideNotFoundError
from app.core.logging import get_logger

logger = get_logger("services.guide")


class GuideService:
    """Service handling interview guide upload, dynamic extraction, and question persistence."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_guide(
        self,
        project_id: UUID,
        filename: str,
        content: bytes,
    ) -> tuple[InterviewGuide, list[ResearchQuestion]]:
        """Process an uploaded guide: save, extract text, call Gemini to extract questions, and persist."""
        p_stmt = select(Project).where(Project.id == project_id)
        p_res = await self.db.execute(p_stmt)
        if not p_res.scalar_one_or_none():
            raise ProjectNotFoundError(project_id)

        rel_path = local_storage.save(project_id, filename, content)

        extracted_text = extract_guide_text(content, filename)

        g_stmt = select(InterviewGuide).where(InterviewGuide.project_id == project_id)
        g_res = await self.db.execute(g_stmt)
        guide = g_res.scalar_one_or_none()

        if guide:
            guide.source_file = rel_path
            guide.status = GuideStatus.PROCESSING.value
            await self.db.execute(
                delete(ResearchQuestion).where(ResearchQuestion.guide_id == guide.id)
            )
        else:
            guide = InterviewGuide(
                project_id=project_id,
                source_file=rel_path,
                status=GuideStatus.PROCESSING.value,
            )
            self.db.add(guide)

        await self.db.flush()
        await self.db.refresh(guide)

        try:
            prompt = GUIDE_EXTRACTION_USER_PROMPT.format(guide_text=extracted_text)
            gemini = get_gemini_client()
            result: GuideExtractionResult = await gemini.generate_structured(
                prompt=prompt,
                response_model=GuideExtractionResult,
                system_prompt=GUIDE_EXTRACTION_SYSTEM_PROMPT,
            )

            questions = []
            for q in result.questions:
                rq = ResearchQuestion(
                    project_id=project_id,
                    guide_id=guide.id,
                    question_number=q.question_number,
                    question_text=q.question_text,
                    category=q.category,
                )
                self.db.add(rq)
                questions.append(rq)

            guide.status = GuideStatus.COMPLETED.value
            await self.db.flush()

            logger.info(
                f"Successfully extracted {len(questions)} research questions from guide",
                extra={"operation": "process_guide", "project_id": str(project_id)},
            )
            return guide, questions

        except Exception as e:
            guide.status = GuideStatus.FAILED.value
            await self.db.flush()
            logger.error(
                f"Failed to extract research questions: {e}",
                extra={"operation": "process_guide", "error": str(e)},
            )
            raise

    async def get_questions(self, project_id: UUID) -> list[ResearchQuestion]:
        """Get all research questions for a project ordered by question_number."""
        stmt = (
            select(ResearchQuestion)
            .where(ResearchQuestion.project_id == project_id)
            .order_by(ResearchQuestion.question_number.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_guide(self, project_id: UUID) -> InterviewGuide:
        """Get the interview guide for a project."""
        stmt = select(InterviewGuide).where(InterviewGuide.project_id == project_id)
        result = await self.db.execute(stmt)
        guide = result.scalar_one_or_none()
        if not guide:
            raise GuideNotFoundError(project_id)
        return guide
