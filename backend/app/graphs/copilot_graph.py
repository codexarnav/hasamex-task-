"""LangGraph workflow for the Research Copilot inquiry and grounded response engine."""
from typing import TypedDict
from uuid import UUID
from langgraph.graph import StateGraph, START, END

from app.ai.gemini import get_gemini_client
from app.ai.prompts.copilot import (
    COPILOT_SYSTEM_PROMPT,
    COPILOT_USER_PROMPT,
)
from app.ai.schemas.copilot import CopilotSynthesisResult
from app.retrieval.search import get_search_service
from app.core.logging import get_logger

logger = get_logger("graphs.copilot")


class CopilotState(TypedDict):
    """LangGraph state for Research Copilot question answering."""
    project_id: str
    query: str
    retrieved_utterances: list[dict]
    evidence_pool: list[dict]
    synthesized_answer: str | None
    referenced_evidence_ids: list[str]
    insufficient_evidence: bool
    grounded: bool
    error: str | None


async def retrieve_relevant_context_node(state: CopilotState) -> dict:
    """Retrieve relevant utterances from Qdrant vector store."""
    try:
        search_service = get_search_service()
        results = await search_service.search_utterances_by_text(
            project_id=UUID(state["project_id"]),
            query=state["query"],
            top_k=20,
        )

        utterances = []
        for r in results:
            utterances.append({
                "utterance_id": str(r.utterance_id),
                "transcript_id": str(r.transcript_id),
                "expert_id": str(r.expert_id),
                "speaker": r.speaker or "Speaker",
                "market": r.market or "Global",
                "timestamp_start": r.timestamp_start,
                "timestamp_end": r.timestamp_end,
                "score": r.score,
                "text": r.text or "",
            })

        return {"retrieved_utterances": utterances}

    except Exception as e:
        logger.error(f"Copilot retrieval failed: {e}", extra={"operation": "copilot_retrieve"})
        return {"retrieved_utterances": [], "error": str(e)}


async def synthesize_answer_node(state: CopilotState) -> dict:
    """Synthesize grounded copilot response with structured citations."""
    evidence_pool = state.get("evidence_pool", [])
    retrieved_utterances = state.get("retrieved_utterances", [])

    if not evidence_pool and not retrieved_utterances:
        return {
            "synthesized_answer": "No relevant transcript data or evidence was found in this project to answer your question.",
            "referenced_evidence_ids": [],
            "insufficient_evidence": True,
            "grounded": True,
        }

    try:
        context_items = []
        for ev in evidence_pool:
            ts = f"[{ev.get('timestamp_start', 'N/A')} - {ev.get('timestamp_end', 'N/A')}]"
            context_items.append(
                f"[Evidence ID: {ev['id']}] Expert: {ev.get('expert_name', 'Unknown')} ({ev.get('market', 'Global')}) {ts}\n"
                f"Quote: \"{ev['quote']}\""
            )

        for utt in retrieved_utterances:
            if "text" in utt and utt["text"]:
                ts = f"[{utt.get('timestamp_start', 'N/A')} - {utt.get('timestamp_end', 'N/A')}]"
                context_items.append(
                    f"[Utterance ID: {utt['utterance_id']}] Speaker: {utt.get('speaker', 'Speaker')} {ts}\n"
                    f"Text: \"{utt['text']}\""
                )

        prompt = COPILOT_USER_PROMPT.format(
            query=state["query"],
            retrieved_context_formatted="\n\n".join(context_items),
        )

        gemini = get_gemini_client()
        result: CopilotSynthesisResult = await gemini.generate_structured(
            prompt=prompt,
            response_model=CopilotSynthesisResult,
            system_prompt=COPILOT_SYSTEM_PROMPT,
        )

        available_ids = {str(ev["id"]) for ev in evidence_pool}
        valid_refs = [
            str(eid) for eid in result.evidence_ids
            if str(eid) in available_ids
        ]
        if not valid_refs and not result.insufficient_evidence and evidence_pool:
            valid_refs = list(available_ids)[:3]

        return {
            "synthesized_answer": result.answer,
            "referenced_evidence_ids": valid_refs,
            "insufficient_evidence": result.insufficient_evidence,
            "grounded": True,
        }

    except Exception as e:
        logger.error(f"Copilot synthesis failed: {e}", extra={"operation": "copilot_synthesize"})
        return {
            "synthesized_answer": "An error occurred while synthesizing the answer from evidence.",
            "referenced_evidence_ids": [],
            "insufficient_evidence": True,
            "grounded": False,
            "error": str(e),
        }


def create_copilot_graph():
    """Build and compile the copilot LangGraph workflow."""
    workflow = StateGraph(CopilotState)

    workflow.add_node("retrieve_relevant_context", retrieve_relevant_context_node)
    workflow.add_node("synthesize_answer", synthesize_answer_node)

    workflow.add_edge(START, "retrieve_relevant_context")
    workflow.add_edge("retrieve_relevant_context", "synthesize_answer")
    workflow.add_edge("synthesize_answer", END)

    return workflow.compile()


copilot_graph = create_copilot_graph()
