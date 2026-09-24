"""Test configuration and shared fixtures with fully mocked AI & Vector services."""
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from httpx import AsyncClient, ASGITransport

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.ai.client import LLMClient
from app.ai.gemini import get_gemini_client
import app.ai.gemini as gemini_module
from app.retrieval.embeddings import EmbeddingService, set_embedding_service
from app.retrieval.qdrant import QdrantRepository, ScoredUtteranceResult, set_qdrant_repository
from app.ai.schemas.guide import GuideExtractionResult, ExtractedQuestion
from app.ai.schemas.evidence import EvidenceExtractionResult, EvidenceCandidate
from app.ai.schemas.answer import AnswerGenerationResult
from app.ai.schemas.difference import DifferenceAnalysisResult, DifferencePerspectiveItem
from app.ai.schemas.insight import InsightGenerationResult, SingleInsight
from app.ai.schemas.copilot import CopilotSynthesisResult

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

test_session_factory = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class MockEmbeddingService(EmbeddingService):
    """Deterministic in-memory embedding service for testing."""

    async def embed_text(self, text: str) -> list[float]:
        val = (float(len(text) % 100) + 1.0) / 100.0
        return [val] * 3072

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [await self.embed_text(t) for t in texts]


class MockQdrantRepository:
    """In-memory vector store mock for testing."""

    def __init__(self):
        self.points: dict[str, dict] = {}

    async def init_collection(self) -> None:
        pass

    async def upsert_utterances(
        self,
        project_id: UUID,
        transcript_id: UUID,
        expert_id: UUID,
        utterance_records: list[dict],
    ) -> None:
        for item in utterance_records:
            uid = str(item["utterance_id"])
            self.points[uid] = {
                "project_id": str(project_id),
                "transcript_id": str(transcript_id),
                "expert_id": str(expert_id),
                "utterance_id": uid,
                "speaker": item.get("speaker"),
                "market": item.get("market"),
                "timestamp_start": item.get("timestamp_start"),
                "timestamp_end": item.get("timestamp_end"),
                "vector": item.get("vector"),
            }

    async def search_utterances(
        self,
        project_id: UUID,
        query_vector: list[float],
        expert_id: UUID | None = None,
        transcript_id: UUID | None = None,
        market: str | None = None,
        top_k: int = 20,
        score_threshold: float | None = None,
    ) -> list[ScoredUtteranceResult]:
        results = []
        for uid, p in self.points.items():
            if p["project_id"] != str(project_id):
                continue
            if expert_id and p["expert_id"] != str(expert_id):
                continue
            if transcript_id and p["transcript_id"] != str(transcript_id):
                continue
            if market and p["market"] != market:
                continue

            results.append(
                ScoredUtteranceResult(
                    utterance_id=UUID(p["utterance_id"]),
                    project_id=UUID(p["project_id"]),
                    expert_id=UUID(p["expert_id"]),
                    transcript_id=UUID(p["transcript_id"]),
                    score=0.92,
                    speaker=p.get("speaker"),
                    market=p.get("market"),
                    timestamp_start=p.get("timestamp_start"),
                    timestamp_end=p.get("timestamp_end"),
                )
            )
        return results[:top_k]

    async def delete_project_vectors(self, project_id: UUID) -> None:
        to_del = [k for k, v in self.points.items() if v["project_id"] == str(project_id)]
        for k in to_del:
            del self.points[k]


class MockGeminiClient(LLMClient):
    """Deterministic Mock Gemini client returning structured outputs for tests."""

    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        return "Mocked plain text response."

    async def generate_structured(self, prompt: str, response_model, system_prompt: str | None = None):
        if response_model == GuideExtractionResult:
            return GuideExtractionResult(
                questions=[
                    ExtractedQuestion(
                        question_number=1,
                        question_text="What are the primary clinical workflows and adoption barriers?",
                        category="Clinical Workflow",
                    ),
                    ExtractedQuestion(
                        question_number=2,
                        question_text="How does reimbursement policy impact procurement decisions?",
                        category="Reimbursement & Economics",
                    ),
                ]
            )

        elif response_model == EvidenceExtractionResult:
            candidates = []
            import re
            uids = re.findall(r'Utterance ID: ([0-9a-fA-F\-]{36})', prompt)
            for uid in uids:
                candidates.append(
                    EvidenceCandidate(
                        utterance_id=UUID(uid),
                        relevant=True,
                        reason="Directly discusses workflow challenges and financial impact",
                        topic="Clinical Workflow",
                        relevance_score=0.95,
                    )
                )
            if not candidates:
                candidates = [
                    EvidenceCandidate(
                        utterance_id=uuid4(),
                        relevant=True,
                        reason="Default relevant snippet",
                        topic="Workflow",
                        relevance_score=0.9,
                    )
                ]
            return EvidenceExtractionResult(candidates=candidates)

        elif response_model == AnswerGenerationResult:
            import re
            eids = [UUID(eid) for eid in re.findall(r'Evidence ID: ([0-9a-fA-F\-]{36})', prompt)]
            return AnswerGenerationResult(
                answer="The expert emphasized that clinical integration requires streamlined protocol adjustments and hospital budget approval.",
                evidence_ids=eids[:2] if eids else [uuid4()],
                is_sufficient=True,
            )

        elif response_model == DifferenceAnalysisResult:
            import re
            eids = [UUID(eid) for eid in re.findall(r'Evidence ID: ([0-9a-fA-F\-]{36})', prompt)]
            exp_ids = [UUID(eid) for eid in re.findall(r'ID: ([0-9a-fA-F\-]{36})', prompt)]
            perspectives = []
            for exp_id in exp_ids:
                perspectives.append(
                    DifferencePerspectiveItem(
                        expert_id=exp_id,
                        perspective="Emphasized distinct regional compliance constraints and procurement timelines.",
                    )
                )
            return DifferenceAnalysisResult(
                difference_detected=True,
                title="Regional Regulatory Divergence",
                description="UK expert focused on NHS centralized procurement, whereas the German expert highlighted strict statutory insurance approval pathways.",
                perspectives=perspectives,
                evidence_ids=eids[:2] if eids else [],
            )

        elif response_model == InsightGenerationResult:
            import re
            eids = [UUID(eid) for eid in re.findall(r'Evidence ID: ([0-9a-fA-F\-]{36})', prompt)]
            return InsightGenerationResult(
                insights=[
                    SingleInsight(
                        title="Decentralized Adoption Friction",
                        summary="Adoption velocity is constrained by localized department budgeting rather than top-down executive resistance.",
                        confidence=0.92,
                        evidence_ids=eids[:2] if eids else [],
                    )
                ]
            )

        elif response_model == CopilotSynthesisResult:
            import re
            eids = [UUID(eid) for eid in re.findall(r'Evidence ID: ([0-9a-fA-F\-]{36})', prompt)]
            return CopilotSynthesisResult(
                answer="According to the transcripts, training requirements and capital costs are the primary determinants of adoption.",
                evidence_ids=eids[:2] if eids else [],
                insufficient_evidence=False,
            )

        return response_model()


@pytest_asyncio.fixture(autouse=True)
async def setup_test_environment():
    """Setup and teardown in-memory test database and mocked services."""
    set_embedding_service(MockEmbeddingService())
    mock_qdrant = MockQdrantRepository()
    set_qdrant_repository(mock_qdrant)

    mock_gemini = MockGeminiClient()
    gemini_module._gemini_client = mock_gemini

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session attached to the test database."""
    async with test_session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an HTTP test client connected to the FastAPI application."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
