"""LangGraph workflow for project-wide research insight synthesis."""
from typing import TypedDict
from uuid import UUID
from langgraph.graph import StateGraph, START, END

from app.ai.gemini import get_gemini_client
from app.ai.prompts.insight_generation import (
    INSIGHT_GENERATION_SYSTEM_PROMPT,
    INSIGHT_GENERATION_USER_PROMPT,
)
from app.ai.schemas.insight import InsightGenerationResult
from app.core.logging import get_logger

logger = get_logger("graphs.insight")


class InsightState(TypedDict):
    """LangGraph state for strategic insight generation."""
    project_id: str
    project_objective: str
    project_findings_summary: str
    available_evidence_ids: list[str]
    generated_insights: list[dict]
    error: str | None


async def generate_insight_node(state: InsightState) -> dict:
    """Synthesize macro strategic insights using Gemini structured generation."""
    try:
        prompt = INSIGHT_GENERATION_USER_PROMPT.format(
            project_objective=state.get("project_objective") or "Qualitative Interview Synthesis",
            project_findings_formatted=state.get("project_findings_summary", ""),
        )

        gemini = get_gemini_client()
        result: InsightGenerationResult = await gemini.generate_structured(
            prompt=prompt,
            response_model=InsightGenerationResult,
            system_prompt=INSIGHT_GENERATION_SYSTEM_PROMPT,
        )

        available_set = set(state.get("available_evidence_ids", []))
        validated_insights = []

        for item in result.insights:
            valid_eids = [
                str(eid) for eid in item.evidence_ids
                if str(eid) in available_set
            ]
            if not valid_eids and state.get("available_evidence_ids"):
                valid_eids = list(available_set)[:3]

            validated_insights.append({
                "title": item.title,
                "summary": item.summary,
                "confidence": float(item.confidence) if item.confidence is not None else 0.85,
                "question_id": str(item.question_id) if item.question_id else None,
                "evidence_ids": valid_eids,
            })

        return {"generated_insights": validated_insights}

    except Exception as e:
        logger.error(f"Insight generation failed: {e}", extra={"operation": "generate_insight"})
        return {"generated_insights": [], "error": str(e)}


def create_insight_graph():
    """Build and compile the insight generation LangGraph workflow."""
    workflow = StateGraph(InsightState)

    workflow.add_node("generate_insight", generate_insight_node)
    workflow.add_edge(START, "generate_insight")
    workflow.add_edge("generate_insight", END)

    return workflow.compile()


insight_graph = create_insight_graph()
