"""LLM client abstraction."""
from abc import ABC, abstractmethod
from typing import TypeVar, Type
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMClient(ABC):
    """Abstract LLM client interface."""

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """Generate a text response.

        Args:
            prompt: The user prompt
            system_prompt: Optional system instructions

        Returns:
            Generated text response
        """
        ...

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: str | None = None,
    ) -> T:
        """Generate a structured response parsed into a Pydantic model.

        Args:
            prompt: The user prompt
            response_model: Pydantic model class for the response
            system_prompt: Optional system instructions

        Returns:
            Parsed Pydantic model instance
        """
        ...
