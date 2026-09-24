"""Tests for ORM model relationships and cascading behaviors."""
import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.project import Project
from app.models.guide import InterviewGuide
from app.models.question import ResearchQuestion
from app.models.expert import Expert
from app.models.transcript import Transcript
from app.models.utterance import Utterance
from app.models.evidence import Evidence
from app.models.answer import Answer
from app.models.difference import Difference, DifferencePerspective
from app.models.insight import Insight


@pytest.mark.asyncio
async def test_project_cascade_delete(db_session: AsyncSession):
    """Verify deleting a project cascades to guides, questions, experts, transcripts, and utterances."""
    project = Project(name="Cascade Test")
    db_session.add(project)
    await db_session.flush()

    guide = InterviewGuide(project_id=project.id, source_file="guide.txt")
    db_session.add(guide)
    await db_session.flush()

    question = ResearchQuestion(
        project_id=project.id,
        guide_id=guide.id,
        question_number=1,
        question_text="Sample Q?",
    )
    db_session.add(question)

    expert = Expert(project_id=project.id, name="Dr. A")
    db_session.add(expert)
    await db_session.flush()

    transcript = Transcript(
        project_id=project.id,
        expert_id=expert.id,
        file_name="t.txt",
        file_path="p",
    )
    db_session.add(transcript)
    await db_session.flush()

    utterance = Utterance(
        transcript_id=transcript.id,
        expert_id=expert.id,
        speaker="Dr. A",
        text="Sample text",
        sequence=0,
    )
    db_session.add(utterance)
    await db_session.flush()

    # Delete project
    await db_session.delete(project)
    await db_session.flush()

    # Verify cascades
    q_res = await db_session.execute(select(ResearchQuestion).where(ResearchQuestion.project_id == project.id))
    assert q_res.scalar_one_or_none() is None

    u_res = await db_session.execute(select(Utterance).where(Utterance.transcript_id == transcript.id))
    assert u_res.scalar_one_or_none() is None
