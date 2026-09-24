"""Interview Guide model."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base
from app.core.enums import GuideStatus


class InterviewGuide(Base):
    __tablename__ = "interview_guides"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False, unique=True,
    )
    source_file: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=GuideStatus.PENDING.value
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    project: Mapped["Project"] = relationship("Project", back_populates="guide")
    questions: Mapped[list["ResearchQuestion"]] = relationship(
        "ResearchQuestion", back_populates="guide", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_interview_guides_project_id", "project_id"),
    )
