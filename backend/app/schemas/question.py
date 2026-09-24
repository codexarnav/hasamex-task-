"""Question schemas."""
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class QuestionResponse(BaseModel):
    id: UUID
    project_id: UUID
    question_number: int
    question_text: str
    category: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class QuestionsListResponse(BaseModel):
    questions: list[QuestionResponse]
    total: int
