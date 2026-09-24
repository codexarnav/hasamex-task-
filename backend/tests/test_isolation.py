"""Tests strictly verifying multi-project data isolation guarantees."""
import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.project import Project
from app.models.expert import Expert
from app.models.transcript import Transcript
from app.models.utterance import Utterance
from app.models.evidence import Evidence
from app.retrieval.qdrant import get_qdrant_repository


@pytest.mark.asyncio
async def test_vector_search_project_isolation(db_session: AsyncSession):
    """Verify Qdrant vector retrieval strictly filters by project_id."""
    project_a_id = uuid4()
    project_b_id = uuid4()
    expert_a_id = uuid4()
    expert_b_id = uuid4()
    transcript_a_id = uuid4()
    transcript_b_id = uuid4()
    utterance_a_id = uuid4()
    utterance_b_id = uuid4()

    qdrant = get_qdrant_repository()

    # Index Project A utterances
    await qdrant.upsert_utterances(
        project_id=project_a_id,
        transcript_id=transcript_a_id,
        expert_id=expert_a_id,
        utterance_records=[
            {
                "utterance_id": utterance_a_id,
                "vector": [0.5] * 3072,
                "speaker": "Expert A",
                "market": "UK",
                "timestamp_start": "00:01:00",
                "timestamp_end": "00:02:00",
            }
        ],
    )

    # Index Project B utterances
    await qdrant.upsert_utterances(
        project_id=project_b_id,
        transcript_id=transcript_b_id,
        expert_id=expert_b_id,
        utterance_records=[
            {
                "utterance_id": utterance_b_id,
                "vector": [0.5] * 3072,
                "speaker": "Expert B",
                "market": "Germany",
                "timestamp_start": "00:05:00",
                "timestamp_end": "00:06:00",
            }
        ],
    )

    # Search scoped to Project A
    results_a = await qdrant.search_utterances(
        project_id=project_a_id,
        query_vector=[0.5] * 3072,
    )
    assert len(results_a) == 1
    assert results_a[0].project_id == project_a_id
    assert results_a[0].utterance_id == utterance_a_id
    assert results_a[0].utterance_id != utterance_b_id

    # Search scoped to Project B
    results_b = await qdrant.search_utterances(
        project_id=project_b_id,
        query_vector=[0.5] * 3072,
    )
    assert len(results_b) == 1
    assert results_b[0].project_id == project_b_id
    assert results_b[0].utterance_id == utterance_b_id
    assert results_b[0].utterance_id != utterance_a_id
