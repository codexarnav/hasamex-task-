"""Difference and DifferencePerspective models."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base
from app.models.evidence import difference_evidence


class Difference(Base):
    __tablename__ = "differences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("research_questions.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="differences")
    question: Mapped["ResearchQuestion"] = relationship("ResearchQuestion", back_populates="differences")
    perspectives: Mapped[list["DifferencePerspective"]] = relationship(
        "DifferencePerspective", back_populates="difference", cascade="all, delete-orphan"
    )
    evidence_items: Mapped[list["Evidence"]] = relationship(
        "Evidence", secondary=difference_evidence, lazy="selectin"
    )

    __table_args__ = (
        Index("ix_differences_project_id", "project_id"),
        Index("ix_differences_question_id", "question_id"),
    )


class DifferencePerspective(Base):
    __tablename__ = "difference_perspectives"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    difference_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("differences.id", ondelete="CASCADE"), nullable=False
    )
    expert_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("experts.id", ondelete="CASCADE"), nullable=False
    )
    perspective: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    difference: Mapped["Difference"] = relationship("Difference", back_populates="perspectives")
    expert: Mapped["Expert"] = relationship("Expert")

    __table_args__ = (
        Index("ix_difference_perspectives_difference_id", "difference_id"),
    )
