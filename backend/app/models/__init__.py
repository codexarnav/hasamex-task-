"""Models package - imports all models to register with SQLAlchemy Base."""
from app.models.project import Project
from app.models.guide import InterviewGuide
from app.models.question import ResearchQuestion
from app.models.expert import Expert
from app.models.transcript import Transcript
from app.models.utterance import Utterance
from app.models.evidence import Evidence, answer_evidence, difference_evidence, insight_evidence
from app.models.answer import Answer
from app.models.difference import Difference
from app.models.insight import Insight

__all__ = [
    "Project",
    "InterviewGuide",
    "ResearchQuestion",
    "Expert",
    "Transcript",
    "Utterance",
    "Evidence",
    "Answer",
    "Difference",
    "Insight",
    "answer_evidence",
    "difference_evidence",
    "insight_evidence",
]
