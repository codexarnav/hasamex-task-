"""Evidence schemas."""
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class TimestampInfo(BaseModel):
    start: str | None
    end: str | None


class ExpertBrief(BaseModel):
    id: UUID
    name: str

    model_config = {"from_attributes": True}


class TranscriptBrief(BaseModel):
    id: UUID
    file_name: str

    model_config = {"from_attributes": True}


class EvidenceResponse(BaseModel):
    id: UUID
    quote: str
    topic: str | None
    relevance_score: float | None
    expert: ExpertBrief
    transcript: TranscriptBrief
    timestamp: TimestampInfo
    created_at: datetime


class EvidenceListResponse(BaseModel):
    evidence: list[EvidenceResponse]
    total: int
