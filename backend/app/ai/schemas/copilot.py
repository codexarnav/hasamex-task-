"""AI schemas for copilot."""
from uuid import UUID
from pydantic import BaseModel, Field


class CopilotSynthesisResult(BaseModel):
    """Structured LLM result for research copilot inquiries."""
    answer: str = Field(..., description="Direct synthesized answer grounded entirely in provided context")
    evidence_ids: list[UUID] = Field(
        default_factory=list,
        description="List of Evidence UUIDs directly referenced in the synthesized answer"
    )
    insufficient_evidence: bool = Field(
        default=False,
        description="Set to True if the retrieved context does not contain adequate evidence to answer the query"
    )
