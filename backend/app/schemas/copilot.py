"""Copilot schemas."""
from uuid import UUID
from pydantic import BaseModel, Field
from app.schemas.evidence import EvidenceResponse


class CopilotRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


class CopilotResponse(BaseModel):
    answer: str
    evidence: list[EvidenceResponse]
    insufficient_evidence: bool
