"""Difference schemas."""
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from app.schemas.evidence import EvidenceResponse


class PerspectiveResponse(BaseModel):
    expert_id: UUID
    expert_name: str
    perspective: str


class DifferenceResponse(BaseModel):
    id: UUID
    project_id: UUID
    question_id: UUID
    title: str | None
    description: str | None
    perspectives: list[PerspectiveResponse]
    evidence: list[EvidenceResponse]
    created_at: datetime


class DifferencesListResponse(BaseModel):
    differences: list[DifferenceResponse]
    total: int
