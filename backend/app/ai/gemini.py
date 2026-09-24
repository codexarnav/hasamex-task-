"""Gemini LLM client implementation."""
import asyncio
import json
from typing import Type, TypeVar

from pydantic import BaseModel
from google import genai
from google.genai import types

from app.ai.client import LLMClient
from app.core.config import get_settings
from app.core.exceptions import LLMError, LLMStructuredOutputError
from app.core.logging import get_logger

logger = get_logger("ai.gemini")
T = TypeVar("T", bound=BaseModel)


class GeminiClient(LLMClient):
    """Google Gemini LLM client."""

    def __init__(self):
        settings = get_settings()
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_MODEL
        self.max_retries = settings.MAX_LLM_RETRIES

    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """Generate a text response from Gemini."""
        try:
            config = types.GenerateContentConfig()
            if system_prompt:
                config.system_instruction = system_prompt

            def _call():
                return self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=config,
                )

            response = await asyncio.to_thread(_call)
            return response.text

        except Exception as e:
            logger.error(
                f"Gemini generation failed: {e}",
                extra={"operation": "llm_generate", "error": str(e)},
            )
            raise LLMError(
                message="LLM generation failed",
                detail=str(e),
            )

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: str | None = None,
    ) -> T:
        """Generate a structured response from Gemini and parse into Pydantic model."""
        last_error: Exception | None = None

        for attempt in range(self.max_retries + 1):
            try:
                config = types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=response_model,
                )
                if system_prompt:
                    config.system_instruction = system_prompt

                def _call():
                    return self.client.models.generate_content(
                        model=self.model,
                        contents=prompt,
                        config=config,
                    )

                response = await asyncio.to_thread(_call)

                raw_text = response.text
                # Parse JSON and validate with Pydantic
                parsed_data = json.loads(raw_text)
                result = response_model.model_validate(parsed_data)

                logger.info(
                    "Structured generation succeeded",
                    extra={
                        "operation": "llm_structured_generate",
                        "detail": response_model.__name__,
                    },
                )
                return result

            except json.JSONDecodeError as e:
                last_error = e
                logger.warning(
                    f"JSON parse failed (attempt {attempt + 1}/{self.max_retries + 1}): {e}",
                    extra={"operation": "llm_structured_generate", "error": str(e)},
                )
            except Exception as e:
                last_error = e
                logger.warning(
                    f"Structured generation failed (attempt {attempt + 1}/{self.max_retries + 1}): {e}",
                    extra={"operation": "llm_structured_generate", "error": str(e)},
                )

        raise LLMStructuredOutputError(
            message="Failed to generate valid structured output after retries",
            detail=str(last_error),
        )


# Singleton
_gemini_client: GeminiClient | None = None


def get_gemini_client() -> GeminiClient:
    """Get or create the Gemini client singleton."""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
