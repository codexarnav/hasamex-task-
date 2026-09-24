"""Evidence model and association tables."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, Float, DateTime, ForeignKey, Index, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base

# Many-to-many: Answer <-> Evidence
answer_evidence = Table(
    "answer_evidence",
    Base.metadata,
    Column("answer_id", UUID(as_uuid=True), ForeignKey("answers.id", ondelete="CASCADE"), primary_key=True),
    Column("evidence_id", UUID(as_uuid=True), ForeignKey("evidence.id", ondelete="CASCADE"), primary_key=True),
)

# Many-to-many: Difference <-> Evidence
difference_evidence = Table(
    "difference_evidence",
    Base.metadata,
    Column("difference_id", UUID(as_uuid=True), ForeignKey("differences.id", ondelete="CASCADE"), primary_key=True),
    Column("evidence_id", UUID(as_uuid=True), ForeignKey("evidence.id", ondelete="CASCADE"), primary_key=True),
)

# Many-to-many: Insight <-> Evidence
insight_evidence = Table(
    "insight_evidence",
    Base.metadata,
    Column("insight_id", UUID(as_uuid=True), ForeignKey("insights.id", ondelete="CASCADE"), primary_key=True),
    Column("evidence_id", UUID(as_uuid=True), ForeignKey("evidence.id", ondelete="CASCADE"), primary_key=True),
)


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("research_questions.id", ondelete="CASCADE"), nullable=False
    )
    transcript_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("transcripts.id", ondelete="CASCADE"), nullable=False
    )
    expert_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("experts.id", ondelete="CASCADE"), nullable=False
    )
    utterance_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("utterances.id", ondelete="CASCADE"), nullable=False
    )
    quote: Mapped[str] = mapped_column(Text, nullable=False)
    topic: Mapped[str | None] = mapped_column(String(500), nullable=True)
    relevance_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="evidence")
    question: Mapped["ResearchQuestion"] = relationship("ResearchQuestion", back_populates="evidence")
    transcript: Mapped["Transcript"] = relationship("Transcript", back_populates="evidence")
    expert: Mapped["Expert"] = relationship("Expert", back_populates="evidence")
    utterance: Mapped["Utterance"] = relationship("Utterance", back_populates="evidence")

    __table_args__ = (
        Index("ix_evidence_project_id", "project_id"),
        Index("ix_evidence_question_id", "question_id"),
        Index("ix_evidence_expert_id", "expert_id"),
        Index("ix_evidence_transcript_id", "transcript_id"),
        Index("ix_evidence_utterance_id", "utterance_id"),
    )
