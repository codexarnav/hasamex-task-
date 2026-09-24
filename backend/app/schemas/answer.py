"""Answer schemas."""
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from app.schemas.evidence import EvidenceResponse


class AnswerResponse(BaseModel):
    id: UUID
    project_id: UUID
    question_id: UUID
    expert_id: UUID
    answer_text: str
    status: str
    evidence: list[EvidenceResponse]
    created_at: datetime
    updated_at: datetime


class AnalysisQuestionResponse(BaseModel):
    question_id: UUID
    question_number: int
    question_text: str
    answers: list[AnswerResponse]


class AnalysisResponse(BaseModel):
    project_id: UUID
    status: str
    questions: list[AnalysisQuestionResponse]
