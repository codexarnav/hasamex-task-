"""LangGraph workflow for expert answer generation with grounded evidence validation."""
from typing import TypedDict
from uuid import UUID
from langgraph.graph import StateGraph, START, END

from app.ai.gemini import get_gemini_client
from app.ai.prompts.answer_generation import (
    ANSWER_GENERATION_SYSTEM_PROMPT,
    ANSWER_GENERATION_USER_PROMPT,
)
from app.ai.schemas.answer import AnswerGenerationResult
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("graphs.answer")


class AnswerState(TypedDict):
    """LangGraph state for expert answer generation."""
    project_id: str
    question_id: str
    expert_id: str
    question_number: int
    question_text: str
    category: str | None
    expert_name: str
    expert_role: str | None
    expert_market: str | None
    available_evidence: list[dict]
    answer_text: str | None
    validated_evidence_ids: list[str]
    is_valid: bool
    retry_count: int
    error: str | None


async def generate_answer_node(state: AnswerState) -> dict:
    """Generate grounded answer using Gemini LLM strictly from provided evidence."""
    evidence_list = state.get("available_evidence", [])

    if not evidence_list:
        return {
            "answer_text": "Insufficient evidence provided in the transcript to address this question.",
            "validated_evidence_ids": [],
            "is_valid": True,
            "error": None,
        }

    try:
        formatted_evidence = []
        for ev in evidence_list:
            ts = f"[{ev.get('timestamp_start', 'N/A')} - {ev.get('timestamp_end', 'N/A')}]"
            formatted_evidence.append(
                f"- Evidence ID: {ev['id']}\n"
                f"  Timestamp: {ts}\n"
                f"  Topic: {ev.get('topic', 'General')}\n"
                f"  Quote: \"{ev['quote']}\""
            )

        prompt = ANSWER_GENERATION_USER_PROMPT.format(
            question_number=state.get("question_number", 1),
            category=state.get("category") or "General",
            question_text=state.get("question_text", ""),
            expert_name=state.get("expert_name", "Expert"),
            expert_role=state.get("expert_role") or "Specialist",
            expert_market=state.get("expert_market") or "Global",
            evidence_formatted="\n\n".join(formatted_evidence),
        )

        gemini = get_gemini_client()
        result: AnswerGenerationResult = await gemini.generate_structured(
            prompt=prompt,
            response_model=AnswerGenerationResult,
            system_prompt=ANSWER_GENERATION_SYSTEM_PROMPT,
        )

        return {
            "answer_text": result.answer,
            "validated_evidence_ids": [str(eid) for eid in result.evidence_ids],
            "retry_count": state.get("retry_count", 0) + 1,
        }

    except Exception as e:
        logger.error(f"Answer generation failed: {e}", extra={"operation": "generate_answer"})
        return {
            "answer_text": None,
            "validated_evidence_ids": [],
            "error": str(e),
            "retry_count": state.get("retry_count", 0) + 1,
        }


def validate_evidence_refs_node(state: AnswerState) -> dict:
    """Validate that all referenced evidence IDs belong strictly to the provided evidence set."""
    available_ids = {str(ev["id"]) for ev in state.get("available_evidence", [])}
    returned_ids = set(state.get("validated_evidence_ids", []))

    if not returned_ids and state.get("available_evidence"):
        return {
            "validated_evidence_ids": list(available_ids),
            "is_valid": True,
        }

    invalid_ids = returned_ids - available_ids
    if invalid_ids:
        logger.warning(
            f"LLM hallucinated evidence IDs: {invalid_ids}. Filtering out invalid IDs.",
            extra={"operation": "validate_evidence_refs"}
        )
        valid_subset = list(returned_ids & available_ids)
        if valid_subset:
            return {
                "validated_evidence_ids": valid_subset,
                "is_valid": True,
            }
        else:
            return {
                "validated_evidence_ids": list(available_ids),
                "is_valid": False,
            }

    return {
        "validated_evidence_ids": list(returned_ids),
        "is_valid": True,
    }


def check_validity_and_retry(state: AnswerState) -> str:
    """Check if answer is valid or if retry limit has been exceeded."""
    if state.get("is_valid") and state.get("answer_text"):
        return "valid"

    max_retries = get_settings().MAX_LLM_RETRIES
    if state.get("retry_count", 0) <= max_retries:
        return "retry"
    return "max_retries_exceeded"


def create_answer_graph():
    """Build and compile the answer LangGraph workflow."""
    workflow = StateGraph(AnswerState)

    workflow.add_node("generate_answer", generate_answer_node)
    workflow.add_node("validate_evidence_refs", validate_evidence_refs_node)

    workflow.add_edge(START, "generate_answer")
    workflow.add_edge("generate_answer", "validate_evidence_refs")

    workflow.add_conditional_edges(
        "validate_evidence_refs",
        check_validity_and_retry,
        {
            "valid": END,
            "retry": "generate_answer",
            "max_retries_exceeded": END,
        }
    )

    return workflow.compile()


answer_graph = create_answer_graph()
