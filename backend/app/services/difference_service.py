"""Cross-expert difference analysis and persistence service."""
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.models.difference import Difference, DifferencePerspective
from app.models.question import ResearchQuestion
from app.models.answer import Answer
from app.models.evidence import Evidence
from app.models.expert import Expert
from app.schemas.difference import DifferenceResponse, PerspectiveResponse
from app.services.evidence_service import EvidenceService
from app.graphs.difference_graph import difference_graph
from app.core.logging import get_logger

logger = get_logger("services.difference")


class DifferenceService:
    """Service handling cross-expert difference analysis and perspective tracking."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.evidence_service = EvidenceService(db)

    async def analyze_differences_for_question(
        self,
        project_id: UUID,
        question: ResearchQuestion,
    ) -> Difference | None:
        """Run difference analysis across experts for a single research question."""
        stmt = (
            select(Answer)
            .where(Answer.project_id == project_id, Answer.question_id == question.id)
            .options(
                selectinload(Answer.expert),
                selectinload(Answer.evidence_items),
            )
        )
        res = await self.db.execute(stmt)
        answers = list(res.scalars().all())

        if len(answers) < 2:
            return None

        expert_answers_input = []
        available_evidence_ids = []

        for ans in answers:
            ev_list = []
            for ev in ans.evidence_items:
                available_evidence_ids.append(str(ev.id))
                ev_list.append({"id": str(ev.id), "quote": ev.quote})

            expert_answers_input.append({
                "expert_id": str(ans.expert_id),
                "expert_name": ans.expert.name if ans.expert else "Expert",
                "market": ans.expert.market if ans.expert else "Global",
                "answer_text": ans.answer_text,
                "evidence": ev_list,
            })

        initial_state = {
            "project_id": str(project_id),
            "question_id": str(question.id),
            "question_number": question.question_number,
            "question_text": question.question_text,
            "category": question.category,
            "expert_answers": expert_answers_input,
            "available_evidence_ids": available_evidence_ids,
            "difference_detected": False,
            "title": None,
            "description": None,
            "perspectives": [],
            "validated_evidence_ids": [],
            "error": None,
        }

        final_state = await difference_graph.ainvoke(initial_state)

        await self.db.execute(
            delete(Difference).where(
                Difference.project_id == project_id,
                Difference.question_id == question.id,
            )
        )

        diff_record = Difference(
            project_id=project_id,
            question_id=question.id,
            title=final_state.get("title") or "Cross-Expert Analysis",
            description=final_state.get("description") or "Analysis completed.",
        )
        self.db.add(diff_record)
        await self.db.flush()
        await self.db.refresh(diff_record)

        for p in final_state.get("perspectives", []):
            try:
                exp_id = UUID(p["expert_id"])
                dp = DifferencePerspective(
                    difference_id=diff_record.id,
                    expert_id=exp_id,
                    perspective=p["perspective"],
                )
                self.db.add(dp)
            except Exception as e:
                logger.warning(f"Failed to add perspective for expert {p.get('expert_id')}: {e}")

        if final_state.get("validated_evidence_ids"):
            valid_uuids = [UUID(eid) for eid in final_state["validated_evidence_ids"]]
            ev_stmt = select(Evidence).where(Evidence.id.in_(valid_uuids))
            ev_res = await self.db.execute(ev_stmt)
            diff_record.evidence_items = list(ev_res.scalars().all())

        await self.db.flush()
        return diff_record

    async def list_differences(self, project_id: UUID) -> list[Difference]:
        """List all differences for a project with loaded perspectives and evidence."""
        stmt = (
            select(Difference)
            .where(Difference.project_id == project_id)
            .options(
                selectinload(Difference.perspectives).selectinload(DifferencePerspective.expert),
                selectinload(Difference.evidence_items).selectinload(Evidence.expert),
                selectinload(Difference.evidence_items).selectinload(Evidence.transcript),
                selectinload(Difference.evidence_items).selectinload(Evidence.utterance),
            )
            .order_by(Difference.created_at.asc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    def format_difference_response(self, diff: Difference) -> DifferenceResponse:
        """Format a Difference ORM object into a Pydantic DifferenceResponse."""
        perspectives = [
            PerspectiveResponse(
                expert_id=p.expert_id,
                expert_name=p.expert.name if p.expert else "Unknown Expert",
                perspective=p.perspective,
            )
            for p in diff.perspectives
        ]

        evidence = [
            self.evidence_service.format_evidence_response(ev)
            for ev in diff.evidence_items
        ]

        return DifferenceResponse(
            id=diff.id,
            project_id=diff.project_id,
            question_id=diff.question_id,
            title=diff.title,
            description=diff.description,
            perspectives=perspectives,
            evidence=evidence,
            created_at=diff.created_at,
        )
