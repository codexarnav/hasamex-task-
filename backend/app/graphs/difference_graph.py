"""LangGraph workflow for cross-expert difference analysis."""
from typing import TypedDict
from uuid import UUID
from langgraph.graph import StateGraph, START, END

from app.ai.gemini import get_gemini_client
from app.ai.prompts.difference_analysis import (
    DIFFERENCE_ANALYSIS_SYSTEM_PROMPT,
    DIFFERENCE_ANALYSIS_USER_PROMPT,
)
from app.ai.schemas.difference import DifferenceAnalysisResult
from app.core.logging import get_logger

logger = get_logger("graphs.difference")


class DifferenceState(TypedDict):
    """LangGraph state for cross-expert difference analysis."""
    project_id: str
    question_id: str
    question_number: int
    question_text: str
    category: str | None
    expert_answers: list[dict]
    available_evidence_ids: list[str]
    difference_detected: bool
    title: str | None
    description: str | None
    perspectives: list[dict]
    validated_evidence_ids: list[str]
    error: str | None


async def compare_perspectives_node(state: DifferenceState) -> dict:
    """Analyze expert answers using Gemini LLM to identify meaningful contrasts."""
    answers = state.get("expert_answers", [])
    if len(answers) < 2:
        return {
            "difference_detected": False,
            "title": "Single Expert Response",
            "description": "Cross-expert comparison requires at least two expert answers.",
            "perspectives": [],
            "validated_evidence_ids": [],
        }

    try:
        formatted_blocks = []
        for ans in answers:
            ev_quotes = []
            for ev in ans.get("evidence", []):
                ev_quotes.append(f"    - [Evidence ID: {ev['id']}]: \"{ev['quote']}\"")
            ev_str = "\n".join(ev_quotes) if ev_quotes else "    (No specific quotes)"

            formatted_blocks.append(
                f"EXPERT: {ans['expert_name']} (Market: {ans.get('market', 'N/A')}, ID: {ans['expert_id']})\n"
                f"ANSWER:\n{ans['answer_text']}\n"
                f"SUPPORTING EVIDENCE:\n{ev_str}"
            )

        prompt = DIFFERENCE_ANALYSIS_USER_PROMPT.format(
            question_number=state.get("question_number", 1),
            category=state.get("category") or "General",
            question_text=state.get("question_text", ""),
            expert_answers_formatted="\n\n---\n\n".join(formatted_blocks),
        )

        gemini = get_gemini_client()
        result: DifferenceAnalysisResult = await gemini.generate_structured(
            prompt=prompt,
            response_model=DifferenceAnalysisResult,
            system_prompt=DIFFERENCE_ANALYSIS_SYSTEM_PROMPT,
        )

        perspectives = [
            {"expert_id": str(p.expert_id), "perspective": p.perspective}
            for p in result.perspectives
        ]

        available_set = set(state.get("available_evidence_ids", []))
        valid_evidence = [
            str(eid) for eid in result.evidence_ids
            if str(eid) in available_set
        ]
        if not valid_evidence and state.get("available_evidence_ids"):
            valid_evidence = list(available_set)[:5]

        return {
            "difference_detected": result.difference_detected,
            "title": result.title if result.difference_detected else "No significant difference detected",
            "description": result.description,
            "perspectives": perspectives,
            "validated_evidence_ids": valid_evidence,
        }

    except Exception as e:
        logger.error(f"Difference comparison failed: {e}", extra={"operation": "compare_perspectives"})
        return {
            "difference_detected": False,
            "title": "Comparison Inconclusive",
            "description": "Automatic comparison encountered an issue.",
            "perspectives": [],
            "validated_evidence_ids": [],
            "error": str(e),
        }


def create_difference_graph():
    """Build and compile the difference analysis LangGraph workflow."""
    workflow = StateGraph(DifferenceState)

    workflow.add_node("compare_perspectives", compare_perspectives_node)
    workflow.add_edge(START, "compare_perspectives")
    workflow.add_edge("compare_perspectives", END)

    return workflow.compile()


difference_graph = create_difference_graph()
