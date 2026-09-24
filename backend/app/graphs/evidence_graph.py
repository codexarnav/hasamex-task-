"""LangGraph workflow for evidence retrieval, LLM validation, and persistence."""
from typing import TypedDict
from uuid import UUID
from langgraph.graph import StateGraph, START, END

from app.ai.gemini import get_gemini_client
from app.ai.prompts.evidence_classification import (
    EVIDENCE_CLASSIFICATION_SYSTEM_PROMPT,
    EVIDENCE_CLASSIFICATION_USER_PROMPT,
)
from app.ai.schemas.evidence import EvidenceExtractionResult
from app.retrieval.search import get_search_service
from app.core.logging import get_logger

logger = get_logger("graphs.evidence")


class EvidenceState(TypedDict):
    """LangGraph state for evidence retrieval & validation workflow."""
    project_id: str
    question_id: str
    expert_id: str
    question_text: str
    question_number: int
    category: str | None
    expert_name: str
    expert_role: str | None
    expert_market: str | None
    candidate_utterances: list[dict]
    classified_evidence: list[dict]
    evidence_ids: list[str]
    is_sufficient: bool
    error: str | None


async def retrieve_candidates_node(state: EvidenceState) -> dict:
    """Retrieve candidate utterances from Qdrant scoped to this project and expert."""
    try:
        search_service = get_search_service()
        results = await search_service.search_utterances_by_text(
            project_id=UUID(state["project_id"]),
            query=state["question_text"],
            expert_id=UUID(state["expert_id"]),
            top_k=15,
        )

        candidates = []
        for r in results:
            candidates.append({
                "utterance_id": str(r.utterance_id),
                "transcript_id": str(r.transcript_id),
                "speaker": r.speaker or "Expert",
                "timestamp_start": r.timestamp_start,
                "timestamp_end": r.timestamp_end,
                "score": r.score,
                "text": r.text or "",
            })

        return {"candidate_utterances": candidates}

    except Exception as e:
        logger.error(f"Candidate retrieval failed: {e}", extra={"operation": "retrieve_candidates"})
        return {"candidate_utterances": [], "error": str(e)}


async def classify_candidates_node(state: EvidenceState) -> dict:
    """Classify candidate utterances with Gemini LLM to filter for genuine qualitative evidence."""
    candidates = state.get("candidate_utterances", [])
    if not candidates:
        return {"classified_evidence": [], "is_sufficient": False}

    try:
        formatted_list = []
        for c in candidates:
            text_snippet = c.get("text", "")
            ts = f"[{c.get('timestamp_start', 'N/A')} - {c.get('timestamp_end', 'N/A')}]"
            formatted_list.append(
                f"- Utterance ID: {c['utterance_id']}\n"
                f"  Speaker: {c['speaker']} {ts}\n"
                f"  Content: \"{text_snippet}\""
            )

        prompt = EVIDENCE_CLASSIFICATION_USER_PROMPT.format(
            question_number=state.get("question_number", 1),
            category=state.get("category") or "General",
            question_text=state.get("question_text", ""),
            expert_name=state.get("expert_name", "Expert"),
            expert_role=state.get("expert_role") or "Specialist",
            expert_market=state.get("expert_market") or "Global",
            candidate_utterances_formatted="\n\n".join(formatted_list),
        )

        gemini = get_gemini_client()
        result: EvidenceExtractionResult = await gemini.generate_structured(
            prompt=prompt,
            response_model=EvidenceExtractionResult,
            system_prompt=EVIDENCE_CLASSIFICATION_SYSTEM_PROMPT,
        )

        candidate_map = {c["utterance_id"]: c for c in candidates}
        classified = []

        for item in result.candidates:
            if item.relevant and str(item.utterance_id) in candidate_map:
                c_meta = candidate_map[str(item.utterance_id)]
                classified.append({
                    "utterance_id": str(item.utterance_id),
                    "transcript_id": c_meta.get("transcript_id"),
                    "quote": c_meta.get("text", ""),
                    "topic": item.topic or state.get("category"),
                    "relevance_score": float(item.relevance_score),
                    "reason": item.reason,
                })

        is_sufficient = len(classified) > 0
        return {
            "classified_evidence": classified,
            "is_sufficient": is_sufficient,
        }

    except Exception as e:
        logger.error(f"Classification failed: {e}", extra={"operation": "classify_candidates"})
        return {"classified_evidence": [], "is_sufficient": False, "error": str(e)}


def check_evidence_sufficiency(state: EvidenceState) -> str:
    """Routing condition based on evidence sufficiency."""
    if state.get("is_sufficient") and state.get("classified_evidence"):
        return "sufficient"
    return "insufficient"


def create_evidence_graph():
    """Build and compile the evidence LangGraph workflow."""
    workflow = StateGraph(EvidenceState)

    workflow.add_node("retrieve_candidates", retrieve_candidates_node)
    workflow.add_node("classify_candidates", classify_candidates_node)

    workflow.add_edge(START, "retrieve_candidates")
    workflow.add_edge("retrieve_candidates", "classify_candidates")

    workflow.add_conditional_edges(
        "classify_candidates",
        check_evidence_sufficiency,
        {
            "sufficient": END,
            "insufficient": END,
        }
    )

    return workflow.compile()


evidence_graph = create_evidence_graph()
