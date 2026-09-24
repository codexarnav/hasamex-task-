"""AI schemas for evidence extraction and classification."""
from uuid import UUID
from pydantic import BaseModel, Field


class EvidenceCandidate(BaseModel):
    """A candidate utterance evaluated for evidence relevance."""
    utterance_id: UUID = Field(..., description="UUID of the evaluated utterance")
    relevant: bool = Field(..., description="True if the utterance provides direct evidence for the research question")
    reason: str = Field(..., description="Brief justification for why the utterance is or is not relevant evidence")
    topic: str | None = Field(None, description="Key topic or concept addressed in this evidence")
    relevance_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Relevance score from 0.0 to 1.0")


class EvidenceExtractionResult(BaseModel):
    """Structured LLM result for evidence candidate evaluation."""
    candidates: list[EvidenceCandidate] = Field(
        default_factory=list,
        description="Evaluated candidates with relevance classifications"
    )
