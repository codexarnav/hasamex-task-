"""Project-level strategic insight synthesis and persistence service."""
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.models.insight import Insight
from app.models.project import Project
from app.models.question import ResearchQuestion
from app.models.answer import Answer
from app.models.difference import Difference
from app.models.evidence import Evidence
from app.schemas.insight import InsightResponse
from app.services.evidence_service import EvidenceService
from app.graphs.insight_graph import insight_graph
from app.core.exceptions import ProjectNotFoundError
from app.core.logging import get_logger

logger = get_logger("services.insight")


class InsightService:
    """Service handling high-level research insight generation across project artifacts."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.evidence_service = EvidenceService(db)

    async def generate_project_insights(self, project_id: UUID) -> list[Insight]:
        """Synthesize project-wide insights based on all answers, differences, and evidence."""
        p_stmt = select(Project).where(Project.id == project_id)
        p_res = await self.db.execute(p_stmt)
        project = p_res.scalar_one_or_none()
        if not project:
            raise ProjectNotFoundError(project_id)

        a_stmt = (
            select(Answer)
            .where(Answer.project_id == project_id)
            .options(selectinload(Answer.expert), selectinload(Answer.question))
        )
        a_res = await self.db.execute(a_stmt)
        answers = list(a_res.scalars().all())

        d_stmt = (
            select(Difference)
            .where(Difference.project_id == project_id)
            .options(selectinload(Difference.perspectives), selectinload(Difference.question))
        )
        d_res = await self.db.execute(d_stmt)
        differences = list(d_res.scalars().all())

        e_stmt = select(Evidence).where(Evidence.project_id == project_id)
        e_res = await self.db.execute(e_stmt)
        all_evidence = list(e_res.scalars().all())
        all_evidence_ids = [str(e.id) for e in all_evidence]

        findings_blocks = []
        for ans in answers:
            q_num = ans.question.question_number if ans.question else "?"
            q_text = ans.question.question_text if ans.question else "N/A"
            exp_name = ans.expert.name if ans.expert else "Expert"
            findings_blocks.append(f"Q#{q_num} ({q_text}) - {exp_name}:\n{ans.answer_text}")

        for diff in differences:
            q_num = diff.question.question_number if diff.question else "?"
            findings_blocks.append(f"Cross-Expert Difference Q#{q_num}: {diff.title}\n{diff.description}")

        initial_state = {
            "project_id": str(project_id),
            "project_objective": project.objective or project.name,
            "project_findings_summary": "\n\n".join(findings_blocks),
            "available_evidence_ids": all_evidence_ids,
            "generated_insights": [],
            "error": None,
        }

        final_state = await insight_graph.ainvoke(initial_state)

        await self.db.execute(delete(Insight).where(Insight.project_id == project_id))

        persisted_insights = []
        for item in final_state.get("generated_insights", []):
            q_uuid = UUID(item["question_id"]) if item.get("question_id") else None

            insight = Insight(
                project_id=project_id,
                question_id=q_uuid,
                title=item["title"],
                summary=item["summary"],
                confidence=item.get("confidence", 0.9),
            )
            self.db.add(insight)
            await self.db.flush()
            await self.db.refresh(insight)

            if item.get("evidence_ids"):
                valid_uuids = [UUID(eid) for eid in item["evidence_ids"]]
                ev_stmt = select(Evidence).where(Evidence.id.in_(valid_uuids))
                ev_res = await self.db.execute(ev_stmt)
                insight.evidence_items = list(ev_res.scalars().all())

            await self.db.flush()
            persisted_insights.append(insight)

        return persisted_insights

    async def list_insights(self, project_id: UUID) -> list[Insight]:
        """List all insights for a project with loaded relationships."""
        stmt = (
            select(Insight)
            .where(Insight.project_id == project_id)
            .options(
                selectinload(Insight.evidence_items).selectinload(Evidence.expert),
                selectinload(Insight.evidence_items).selectinload(Evidence.transcript),
                selectinload(Insight.evidence_items).selectinload(Evidence.utterance),
            )
            .order_by(Insight.created_at.asc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    def format_insight_response(self, insight: Insight) -> InsightResponse:
        """Format an Insight ORM entity into a clean Pydantic response."""
        evidence = [
            self.evidence_service.format_evidence_response(ev)
            for ev in insight.evidence_items
        ]
        return InsightResponse(
            id=insight.id,
            project_id=insight.project_id,
            question_id=insight.question_id,
            title=insight.title,
            summary=insight.summary,
            confidence=insight.confidence,
            evidence=evidence,
            created_at=insight.created_at,
        )
