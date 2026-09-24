"""AI schemas for difference analysis."""
from uuid import UUID
from pydantic import BaseModel, Field


class DifferencePerspectiveItem(BaseModel):
    """Specific expert's distinct perspective on a difference."""
    expert_id: UUID = Field(..., description="UUID of the expert")
    perspective: str = Field(..., description="Concise summary of this expert's perspective/stance")


class DifferenceAnalysisResult(BaseModel):
    """Structured LLM result for comparing expert perspectives on a question."""
    difference_detected: bool = Field(
        ...,
        description="True if there is a meaningful, substantive difference in stance/context among experts"
    )
    title: str | None = Field(
        None,
        description="Concise title summarizing the primary point of divergence (if difference_detected=True)"
    )
    description: str | None = Field(
        None,
        description="Detailed explanation of the differences between expert perspectives"
    )
    perspectives: list[DifferencePerspectiveItem] = Field(
        default_factory=list,
        description="Breakdown of each expert's individual perspective"
    )
    evidence_ids: list[UUID] = Field(
        default_factory=list,
        description="UUIDs of evidence items supporting this difference analysis"
    )
