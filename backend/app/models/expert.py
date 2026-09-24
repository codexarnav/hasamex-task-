"""Expert model."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Expert(Base):
    __tablename__ = "experts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str | None] = mapped_column(String(255), nullable=True)
    market: Mapped[str | None] = mapped_column(String(255), nullable=True)
    organization: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    project: Mapped["Project"] = relationship("Project", back_populates="experts")
    transcripts: Mapped[list["Transcript"]] = relationship(
        "Transcript", back_populates="expert", cascade="all, delete-orphan"
    )
    utterances: Mapped[list["Utterance"]] = relationship(
        "Utterance", back_populates="expert", cascade="all, delete-orphan"
    )
    evidence: Mapped[list["Evidence"]] = relationship(
        "Evidence", back_populates="expert", cascade="all, delete-orphan"
    )
    answers: Mapped[list["Answer"]] = relationship(
        "Answer", back_populates="expert", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_experts_project_id", "project_id"),
    )
