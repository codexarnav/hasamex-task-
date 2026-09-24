"""AI schemas for insight generation."""
from uuid import UUID
from pydantic import BaseModel, Field


class SingleInsight(BaseModel):
    """A single higher-level research insight."""
    question_id: UUID | None = Field(None, description="Optional UUID of the specific research question, if localized")
    title: str = Field(..., description="High-level insight title summarizing the synthesized finding")
    summary: str = Field(..., description="Detailed narrative explaining the strategic or research insight")
    confidence: float = Field(default=0.9, ge=0.0, le=1.0, description="Confidence level grounded in evidence depth")
    evidence_ids: list[UUID] = Field(
        default_factory=list,
        description="List of supporting Evidence UUIDs backing this insight"
    )


class InsightGenerationResult(BaseModel):
    """Structured LLM result for synthesized project insights."""
    insights: list[SingleInsight] = Field(
        default_factory=list,
        description="Synthesized strategic research insights"
    )
