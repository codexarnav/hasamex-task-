"""AI schemas for answer generation."""
from uuid import UUID
from pydantic import BaseModel, Field


class AnswerGenerationResult(BaseModel):
    """Structured LLM result for expert answer generation."""
    answer: str = Field(..., description="Grounded, concise answer based strictly on supplied evidence")
    evidence_ids: list[UUID] = Field(
        default_factory=list,
        description="List of Evidence UUIDs directly supporting this answer"
    )
    is_sufficient: bool = Field(
        default=True,
        description="True if supplied evidence was sufficient to formulate an answer, False if evidence is insufficient"
    )
