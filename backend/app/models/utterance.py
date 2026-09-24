"""Utterance model - the most important source-of-truth entity."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Utterance(Base):
    __tablename__ = "utterances"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    transcript_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("transcripts.id", ondelete="CASCADE"), nullable=False
    )
    expert_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("experts.id", ondelete="CASCADE"), nullable=False
    )
    speaker: Mapped[str] = mapped_column(String(255), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp_start: Mapped[str | None] = mapped_column(String(20), nullable=True)
    timestamp_end: Mapped[str | None] = mapped_column(String(20), nullable=True)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    transcript: Mapped["Transcript"] = relationship("Transcript", back_populates="utterances")
    expert: Mapped["Expert"] = relationship("Expert", back_populates="utterances")
    evidence: Mapped[list["Evidence"]] = relationship(
        "Evidence", back_populates="utterance", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_utterances_transcript_id", "transcript_id"),
        Index("ix_utterances_expert_id", "expert_id"),
        Index("ix_utterances_sequence", "transcript_id", "sequence"),
    )
