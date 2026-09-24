"""Embedding service abstraction and Gemini implementation."""
from abc import ABC, abstractmethod
import asyncio
from google import genai
from google.genai import types

from app.core.config import get_settings
from app.core.exceptions import EmbeddingError
from app.core.logging import get_logger

logger = get_logger("retrieval.embeddings")


class EmbeddingService(ABC):
    """Abstract interface for generating vector embeddings."""

    @abstractmethod
    async def embed_text(self, text: str) -> list[float]:
        """Generate embedding vector for a single text."""
        ...

    @abstractmethod
    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embedding vectors for a batch of texts."""
        ...


class GeminiEmbeddingService(EmbeddingService):
    """Gemini-based embedding service using google-genai."""

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION
        self._client: genai.Client | None = None

    def _get_client(self) -> genai.Client:
        if self._client is None:
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    async def embed_text(self, text: str) -> list[float]:
        """Embed a single text string."""
        batch_res = await self.embed_batch([text])
        if not batch_res:
            raise EmbeddingError("Empty embedding returned from provider")
        return batch_res[0]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of text strings individually in parallel."""
        if not texts:
            return []

        sanitized_texts = [t if t and t.strip() else " " for t in texts]

        try:
            client = self._get_client()
            semaphore = asyncio.Semaphore(10)

            async def _embed_single(t: str) -> list[float]:
                async with semaphore:
                    def _call():
                        res = client.models.embed_content(
                            model=self.model,
                            contents=t,
                        )
                        return res.embeddings[0].values
                    return await asyncio.to_thread(_call)

            tasks = [_embed_single(t) for t in sanitized_texts]
            embeddings = await asyncio.gather(*tasks)
            return list(embeddings)

        except Exception as e:
            logger.error(
                f"Embedding generation failed: {e}",
                extra={"operation": "embed_batch", "error": str(e)},
            )
            raise EmbeddingError(
                message="Failed to generate embeddings",
                detail=str(e),
            )


_embedding_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    """Get the embedding service singleton instance."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = GeminiEmbeddingService()
    return _embedding_service


def set_embedding_service(service: EmbeddingService) -> None:
    """Override embedding service (useful for testing)."""
    global _embedding_service
    _embedding_service = service
