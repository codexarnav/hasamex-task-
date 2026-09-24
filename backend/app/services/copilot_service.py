"""Research Copilot inquiry and grounded response resolution service."""
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.project import Project
from app.models.evidence import Evidence
from app.models.utterance import Utterance
from app.models.transcript import Transcript
from app.schemas.copilot import CopilotResponse
from app.services.evidence_service import EvidenceService
from app.graphs.copilot_graph import copilot_graph
from app.core.exceptions import ProjectNotFoundError
from app.core.logging import get_logger

logger = get_logger("services.copilot")


class CopilotService:
    """Service handling ad-hoc researcher inquiries and generating grounded responses."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.evidence_service = EvidenceService(db)

    async def ask(self, project_id: UUID, question: str) -> CopilotResponse:
        """Process an arbitrary researcher query with dynamic retrieval and grounded synthesis."""
        p_stmt = select(Project).where(Project.id == project_id)
        p_res = await self.db.execute(p_stmt)
        if not p_res.scalar_one_or_none():
            raise ProjectNotFoundError(project_id)

        ev_stmt = (
            select(Evidence)
            .where(Evidence.project_id == project_id)
            .options(
                selectinload(Evidence.expert),
                selectinload(Evidence.transcript),
                selectinload(Evidence.utterance),
            )
        )
        ev_res = await self.db.execute(ev_stmt)
        evidence_records = list(ev_res.scalars().all())

        evidence_pool = [
            {
                "id": str(ev.id),
                "quote": ev.quote,
                "topic": ev.topic,
                "expert_name": ev.expert.name if ev.expert else "Expert",
                "market": ev.expert.market if ev.expert else "Global",
                "timestamp_start": ev.utterance.timestamp_start if ev.utterance else None,
                "timestamp_end": ev.utterance.timestamp_end if ev.utterance else None,
            }
            for ev in evidence_records
        ]

        u_stmt = select(Utterance).join(Transcript).where(Transcript.project_id == project_id)
        u_res = await self.db.execute(u_stmt)
        utterance_map = {str(u.id): u for u in u_res.scalars().all()}

        initial_state = {
            "project_id": str(project_id),
            "query": question,
            "retrieved_utterances": [],
            "evidence_pool": evidence_pool,
            "synthesized_answer": None,
            "referenced_evidence_ids": [],
            "insufficient_evidence": False,
            "grounded": True,
            "error": None,
        }

        final_state = await copilot_graph.ainvoke(initial_state)

        if final_state.get("retrieved_utterances") and not final_state.get("synthesized_answer"):
            for u in final_state["retrieved_utterances"]:
                u_obj = utterance_map.get(u["utterance_id"])
                if u_obj:
                    u["text"] = u_obj.text

            from app.graphs.copilot_graph import synthesize_answer_node
            synth_res = await synthesize_answer_node(final_state)
            final_state.update(synth_res)

        ref_ids = final_state.get("referenced_evidence_ids", [])
        resolved_evidence = []

        if ref_ids:
            valid_uuids = [UUID(eid) for eid in ref_ids]
            res_stmt = (
                select(Evidence)
                .where(Evidence.id.in_(valid_uuids))
                .options(
                    selectinload(Evidence.expert),
                    selectinload(Evidence.transcript),
                    selectinload(Evidence.utterance),
                )
            )
            res_res = await self.db.execute(res_stmt)
            for ev in res_res.scalars().all():
                resolved_evidence.append(self.evidence_service.format_evidence_response(ev))

        return CopilotResponse(
            answer=final_state.get("synthesized_answer") or "No answer could be formed.",
            evidence=resolved_evidence,
            insufficient_evidence=final_state.get("insufficient_evidence", False),
        )
