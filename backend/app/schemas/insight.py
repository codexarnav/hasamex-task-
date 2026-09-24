"""Insight schemas."""
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from app.schemas.evidence import EvidenceResponse


class InsightResponse(BaseModel):
    id: UUID
    project_id: UUID
    question_id: UUID | None
    title: str
    summary: str
    confidence: float | None
    evidence: list[EvidenceResponse]
    created_at: datetime


class InsightsListResponse(BaseModel):
    insights: list[InsightResponse]
    total: int
