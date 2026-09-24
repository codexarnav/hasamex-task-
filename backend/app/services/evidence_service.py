"""Evidence management and provenance resolution service."""
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.evidence import Evidence
from app.models.utterance import Utterance
from app.models.expert import Expert
from app.models.transcript import Transcript
from app.schemas.evidence import EvidenceResponse, ExpertBrief, TranscriptBrief, TimestampInfo
from app.core.exceptions import EvidenceNotFoundError
from app.core.logging import get_logger

logger = get_logger("services.evidence")


class EvidenceService:
    """Service handling evidence persistence, retrieval, and provenance formatting."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_evidence(
        self,
        project_id: UUID,
        question_id: UUID,
        transcript_id: UUID,
        expert_id: UUID,
        utterance_id: UUID,
        topic: str | None = None,
        relevance_score: float | None = 1.0,
    ) -> Evidence:
        """Create an evidence record resolving the quote text directly from the source utterance."""
        # Fetch canonical quote from Utterance (Anti-hallucination Rule: quote must originate from DB)
        u_stmt = select(Utterance).where(Utterance.id == utterance_id)
        u_res = await self.db.execute(u_stmt)
        utterance = u_res.scalar_one_or_none()
        if not utterance:
            raise ValueError(f"Referenced utterance {utterance_id} does not exist in database")

        evidence = Evidence(
            project_id=project_id,
            question_id=question_id,
            transcript_id=transcript_id,
            expert_id=expert_id,
            utterance_id=utterance_id,
            quote=utterance.text,  # Exact source quote from DB
            topic=topic,
            relevance_score=relevance_score,
        )
        self.db.add(evidence)
        await self.db.flush()
        await self.db.refresh(evidence)
        return evidence

    async def get_evidence(self, evidence_id: UUID) -> Evidence:
        """Get evidence by ID with loaded relationships."""
        stmt = (
            select(Evidence)
            .where(Evidence.id == evidence_id)
            .options(
                selectinload(Evidence.expert),
                selectinload(Evidence.transcript),
                selectinload(Evidence.utterance),
            )
        )
        res = await self.db.execute(stmt)
        ev = res.scalar_one_or_none()
        if not ev:
            raise EvidenceNotFoundError(evidence_id)
        return ev

    async def list_project_evidence(self, project_id: UUID) -> list[Evidence]:
        """List all evidence records for a project with full relationship data."""
        stmt = (
            select(Evidence)
            .where(Evidence.project_id == project_id)
            .options(
                selectinload(Evidence.expert),
                selectinload(Evidence.transcript),
                selectinload(Evidence.utterance),
            )
            .order_by(Evidence.created_at.asc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    def format_evidence_response(ev: Evidence) -> EvidenceResponse:
        """Format an Evidence model instance into a full EvidenceResponse schema with provenance."""
        return EvidenceResponse(
            id=ev.id,
            quote=ev.quote,
            topic=ev.topic,
            relevance_score=ev.relevance_score,
            expert=ExpertBrief(
                id=ev.expert_id,
                name=ev.expert.name if ev.expert else "Unknown Expert",
            ),
            transcript=TranscriptBrief(
                id=ev.transcript_id,
                file_name=ev.transcript.file_name if ev.transcript else "Unknown Transcript",
            ),
            timestamp=TimestampInfo(
                start=ev.utterance.timestamp_start if ev.utterance else None,
                end=ev.utterance.timestamp_end if ev.utterance else None,
            ),
            created_at=ev.created_at,
        )
