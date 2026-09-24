"""AI schemas for guide extraction."""
from pydantic import BaseModel, Field


class ExtractedQuestion(BaseModel):
    """A single research question extracted from the interview guide."""
    question_number: int = Field(..., description="Sequential question number")
    question_text: str = Field(..., description="The full text of the research question")
    category: str | None = Field(None, description="Optional category or theme for this question")


class GuideExtractionResult(BaseModel):
    """Result of extracting research questions from an interview guide."""
    questions: list[ExtractedQuestion] = Field(..., description="List of extracted research questions")
