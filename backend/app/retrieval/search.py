"""High-level semantic search and retrieval service."""
from uuid import UUID
from app.retrieval.embeddings import get_embedding_service, EmbeddingService
from app.retrieval.qdrant import get_qdrant_repository, QdrantRepository, ScoredUtteranceResult
from app.core.logging import get_logger

logger = get_logger("retrieval.search")


class SemanticSearchService:
    """Service combining embedding generation and Qdrant semantic retrieval."""

    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
        qdrant_repo: QdrantRepository | None = None,
    ):
        self.embedding_service = embedding_service or get_embedding_service()
        self.qdrant_repo = qdrant_repo or get_qdrant_repository()

    async def search_utterances_by_text(
        self,
        project_id: UUID,
        query: str,
        expert_id: UUID | None = None,
        transcript_id: UUID | None = None,
        market: str | None = None,
        top_k: int = 20,
    ) -> list[ScoredUtteranceResult]:
        """Embed text query and search utterances in Qdrant strictly within project bounds."""
        query_vector = await self.embedding_service.embed_text(query)
        results = await self.qdrant_repo.search_utterances(
            project_id=project_id,
            query_vector=query_vector,
            expert_id=expert_id,
            transcript_id=transcript_id,
            market=market,
            top_k=top_k,
        )
        return results


_search_service: SemanticSearchService | None = None


def get_search_service() -> SemanticSearchService:
    """Get the search service singleton instance."""
    global _search_service
    if _search_service is None:
        _search_service = SemanticSearchService()
    return _search_service
