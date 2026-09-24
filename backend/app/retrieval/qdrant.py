"""Qdrant vector database repository."""
from uuid import UUID
from dataclasses import dataclass
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as rest_models
from qdrant_client.http.exceptions import UnexpectedResponse

from app.core.config import get_settings
from app.core.exceptions import VectorStoreError
from app.core.logging import get_logger

logger = get_logger("retrieval.qdrant")


@dataclass
class ScoredUtteranceResult:
    """Search match result from Qdrant vector retrieval."""
    utterance_id: UUID
    project_id: UUID
    expert_id: UUID
    transcript_id: UUID
    score: float
    speaker: str | None = None
    market: str | None = None
    timestamp_start: str | None = None
    timestamp_end: str | None = None
    text: str | None = None


class QdrantRepository:
    """Manages utterance vector indexing and filtered semantic retrieval in Qdrant."""

    def __init__(self, client: AsyncQdrantClient | None = None):
        settings = get_settings()
        self.url = settings.QDRANT_URL
        self.collection_name = settings.QDRANT_COLLECTION
        self.vector_size = settings.EMBEDDING_DIMENSION
        self.client = client or AsyncQdrantClient(
            url=self.url,
            api_key=settings.QDRANT_API_KEY,
        )

    async def init_collection(self) -> None:
        """Ensure the research utterances collection exists with appropriate index settings."""
        try:
            collections = await self.client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if self.collection_name not in collection_names:
                await self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=rest_models.VectorParams(
                        size=self.vector_size,
                        distance=rest_models.Distance.COSINE,
                    ),
                )
                # Create payload indexes for project_id, expert_id, transcript_id
                for field_name in ["project_id", "expert_id", "transcript_id", "market"]:
                    await self.client.create_payload_index(
                        collection_name=self.collection_name,
                        field_name=field_name,
                        field_schema=rest_models.PayloadSchemaType.KEYWORD,
                    )
                logger.info(
                    f"Created Qdrant collection '{self.collection_name}' with indexes",
                    extra={"operation": "init_collection"},
                )
        except Exception as e:
            logger.error(
                f"Failed to initialize Qdrant collection: {e}",
                extra={"operation": "init_collection", "error": str(e)},
            )
            raise VectorStoreError(
                message="Failed to initialize vector database collection",
                detail=str(e),
            )

    async def upsert_utterances(
        self,
        project_id: UUID,
        transcript_id: UUID,
        expert_id: UUID,
        utterance_records: list[dict],
    ) -> None:
        """Upsert a batch of utterance vectors and payloads into Qdrant.

        Each item in utterance_records should contain:
        - utterance_id: UUID
        - vector: list[float]
        - speaker: str
        - market: str | None
        - timestamp_start: str | None
        - timestamp_end: str | None
        """
        if not utterance_records:
            return

        points = []
        for item in utterance_records:
            uid = item["utterance_id"]
            point = rest_models.PointStruct(
                id=str(uid),
                vector=item["vector"],
                payload={
                    "project_id": str(project_id),
                    "transcript_id": str(transcript_id),
                    "expert_id": str(expert_id),
                    "utterance_id": str(uid),
                    "speaker": item.get("speaker"),
                    "market": item.get("market"),
                    "timestamp_start": item.get("timestamp_start"),
                    "timestamp_end": item.get("timestamp_end"),
                    "text": item.get("text"),
                },
            )
            points.append(point)

        try:
            await self.client.upsert(
                collection_name=self.collection_name,
                points=points,
                wait=True,
            )
            logger.info(
                f"Indexed {len(points)} utterances in Qdrant for transcript {transcript_id}",
                extra={"operation": "upsert_utterances", "project_id": str(project_id)},
            )
        except Exception as e:
            logger.error(
                f"Failed to upsert points into Qdrant: {e}",
                extra={"operation": "upsert_utterances", "error": str(e)},
            )
            raise VectorStoreError(
                message="Failed to index utterances in vector store",
                detail=str(e),
            )

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
        """Perform project-isolated semantic search on utterances.

        RULE: All searches MUST filter by project_id to ensure complete data isolation.
        """
        must_conditions: list[rest_models.Condition] = [
            rest_models.FieldCondition(
                key="project_id",
                match=rest_models.MatchValue(value=str(project_id)),
            )
        ]

        if expert_id:
            must_conditions.append(
                rest_models.FieldCondition(
                    key="expert_id",
                    match=rest_models.MatchValue(value=str(expert_id)),
                )
            )

        if transcript_id:
            must_conditions.append(
                rest_models.FieldCondition(
                    key="transcript_id",
                    match=rest_models.MatchValue(value=str(transcript_id)),
                )
            )

        if market:
            must_conditions.append(
                rest_models.FieldCondition(
                    key="market",
                    match=rest_models.MatchValue(value=market),
                )
            )

        qdrant_filter = rest_models.Filter(must=must_conditions)

        try:
            if hasattr(self.client, "query_points"):
                response = await self.client.query_points(
                    collection_name=self.collection_name,
                    query=query_vector,
                    query_filter=qdrant_filter,
                    limit=top_k,
                    score_threshold=score_threshold,
                )
                hits = response.points
            else:
                hits = await self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    query_filter=qdrant_filter,
                    limit=top_k,
                    score_threshold=score_threshold,
                )

            output: list[ScoredUtteranceResult] = []
            for hit in hits:
                payload = hit.payload or {}
                output.append(
                    ScoredUtteranceResult(
                        utterance_id=UUID(payload["utterance_id"]),
                        project_id=UUID(payload["project_id"]),
                        expert_id=UUID(payload["expert_id"]),
                        transcript_id=UUID(payload["transcript_id"]),
                        score=hit.score,
                        speaker=payload.get("speaker"),
                        market=payload.get("market"),
                        timestamp_start=payload.get("timestamp_start"),
                        timestamp_end=payload.get("timestamp_end"),
                        text=payload.get("text"),
                    )
                )

            return output

        except Exception as e:
            logger.error(
                f"Qdrant vector search failed: {e}",
                extra={
                    "operation": "search_utterances",
                    "project_id": str(project_id),
                    "error": str(e),
                },
            )
            raise VectorStoreError(
                message="Vector search query failed",
                detail=str(e),
            )

    async def delete_project_vectors(self, project_id: UUID) -> None:
        """Delete all indexed vectors belonging to a project."""
        try:
            await self.client.delete(
                collection_name=self.collection_name,
                points_selector=rest_models.FilterSelector(
                    filter=rest_models.Filter(
                        must=[
                            rest_models.FieldCondition(
                                key="project_id",
                                match=rest_models.MatchValue(value=str(project_id)),
                            )
                        ]
                    )
                ),
            )
        except Exception as e:
            logger.warning(f"Error deleting vectors for project {project_id}: {e}")

    async def delete_transcript_vectors(self, project_id: UUID, transcript_id: UUID) -> None:
        """Delete all indexed vectors belonging to a specific transcript."""
        try:
            await self.client.delete(
                collection_name=self.collection_name,
                points_selector=rest_models.FilterSelector(
                    filter=rest_models.Filter(
                        must=[
                            rest_models.FieldCondition(
                                key="project_id",
                                match=rest_models.MatchValue(value=str(project_id)),
                            ),
                            rest_models.FieldCondition(
                                key="transcript_id",
                                match=rest_models.MatchValue(value=str(transcript_id)),
                            ),
                        ]
                    )
                ),
            )
            logger.info(
                f"Deleted vectors for transcript {transcript_id}",
                extra={"operation": "delete_transcript_vectors", "project_id": str(project_id)},
            )
        except Exception as e:
            logger.warning(f"Error deleting vectors for transcript {transcript_id}: {e}")


# Singleton
_qdrant_repo: QdrantRepository | None = None


def get_qdrant_repository() -> QdrantRepository:
    """Get the QdrantRepository singleton instance."""
    global _qdrant_repo
    if _qdrant_repo is None:
        _qdrant_repo = QdrantRepository()
    return _qdrant_repo


def set_qdrant_repository(repo: QdrantRepository) -> None:
    """Override repository for tests."""
    global _qdrant_repo
    _qdrant_repo = repo
