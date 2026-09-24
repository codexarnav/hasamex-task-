"""Tests for evidence provenance and anti-hallucination validation rules."""
import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.guide import InterviewGuide
from app.models.question import ResearchQuestion
from app.models.expert import Expert
from app.models.transcript import Transcript
from app.models.utterance import Utterance
from app.services.evidence_service import EvidenceService
from app.graphs.answer_graph import validate_evidence_refs_node


@pytest.mark.asyncio
async def test_evidence_quote_originates_from_database(db_session: AsyncSession):
    """RULE 6: Quotes shown to user MUST originate from stored utterance text, not LLM fabrication."""
    project = Project(name="Grounding Test Project")
    db_session.add(project)
    await db_session.flush()

    guide = InterviewGuide(project_id=project.id, source_file="dummy.txt")
    db_session.add(guide)
    await db_session.flush()

    question = ResearchQuestion(
        project_id=project.id,
        guide_id=guide.id,
        question_number=1,
        question_text="What are adoption hurdles?",
    )
    db_session.add(question)

    expert = Expert(project_id=project.id, name="Dr. Marcus Bell", market="UK")
    db_session.add(expert)
    await db_session.flush()

    transcript = Transcript(
        project_id=project.id,
        expert_id=expert.id,
        file_name="transcript.txt",
        file_path="dummy_path",
    )
    db_session.add(transcript)
    await db_session.flush()

    real_text = "The capital investment for the robotic console exceeded our annual capex ceiling."
    utterance = Utterance(
        transcript_id=transcript.id,
        expert_id=expert.id,
        speaker="Dr. Marcus Bell",
        text=real_text,
        timestamp_start="00:04:12",
        timestamp_end="00:04:35",
        sequence=0,
    )
    db_session.add(utterance)
    await db_session.flush()

    evidence_service = EvidenceService(db_session)
    evidence = await evidence_service.create_evidence(
        project_id=project.id,
        question_id=question.id,
        transcript_id=transcript.id,
        expert_id=expert.id,
        utterance_id=utterance.id,
        topic="Capex Barrier",
        relevance_score=0.98,
    )

    assert evidence.quote == real_text
    assert evidence.utterance_id == utterance.id


def test_answer_validation_filters_hallucinated_ids():
    """RULE 5 & RULE 10: Answer graph must reject hallucinated evidence IDs."""
    real_id_1 = str(uuid4())
    real_id_2 = str(uuid4())
    fake_id = str(uuid4())

    state = {
        "available_evidence": [
            {"id": real_id_1, "quote": "Valid quote 1"},
            {"id": real_id_2, "quote": "Valid quote 2"},
        ],
        "validated_evidence_ids": [real_id_1, fake_id],
    }

    result = validate_evidence_refs_node(state)
    assert result["is_valid"] is True
    assert real_id_1 in result["validated_evidence_ids"]
    assert fake_id not in result["validated_evidence_ids"]
