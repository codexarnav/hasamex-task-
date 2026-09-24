"""Full research analysis orchestration service."""
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.models.project import Project
from app.models.question import ResearchQuestion
from app.models.expert import Expert
from app.models.transcript import Transcript
from app.models.utterance import Utterance
from app.models.evidence import Evidence
from app.models.answer import Answer
from app.schemas.answer import AnswerResponse, AnalysisQuestionResponse, AnalysisResponse
from app.services.evidence_service import EvidenceService
from app.services.difference_service import DifferenceService
from app.services.insight_service import InsightService
from app.graphs.evidence_graph import evidence_graph
from app.graphs.answer_graph import answer_graph
from app.core.enums import ProjectStatus, AnalysisStatus
from app.core.exceptions import ProjectNotFoundError, AnalysisError
from app.core.logging import get_logger

logger = get_logger("services.analysis")


class AnalysisService:
    """Service orchestrating the end-to-end qualitative research analysis pipeline."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.evidence_service = EvidenceService(db)
        self.difference_service = DifferenceService(db)
        self.insight_service = InsightService(db)

    async def run_full_analysis(self, project_id: UUID, transcript_ids: list[UUID] | None = None) -> AnalysisResponse:
        """Run complete analysis pipeline:
        1. Questions x Experts -> Evidence extraction & classification
        2. Questions x Experts -> Grounded answer generation
        3. Questions -> Cross-expert difference analysis
        4. Project -> Strategic insight synthesis

        Args:
            project_id: The project to analyze.
            transcript_ids: Optional list of specific transcript IDs to scope analysis to.
                           When provided, only experts/utterances from these transcripts are used.
        """
        # 1. Fetch project
        p_stmt = select(Project).where(Project.id == project_id)
        p_res = await self.db.execute(p_stmt)
        project = p_res.scalar_one_or_none()
        if not project:
            raise ProjectNotFoundError(project_id)

        project.status = ProjectStatus.PROCESSING.value
        await self.db.flush()

        try:
            # 2. Fetch questions and experts
            q_stmt = (
                select(ResearchQuestion)
                .where(ResearchQuestion.project_id == project_id)
                .order_by(ResearchQuestion.question_number.asc())
            )
            q_res = await self.db.execute(q_stmt)
            questions = list(q_res.scalars().all())

            if not questions:
                raise AnalysisError("No research questions found for project. Please upload an interview guide first.")

            # If transcript_ids are specified, find the experts linked to those transcripts
            if transcript_ids:
                t_stmt = (
                    select(Transcript)
                    .where(
                        Transcript.project_id == project_id,
                        Transcript.id.in_(transcript_ids),
                    )
                )
                t_res = await self.db.execute(t_stmt)
                selected_transcripts = list(t_res.scalars().all())

                if not selected_transcripts:
                    raise AnalysisError("None of the selected transcripts were found in this project.")

                # Get unique expert IDs from selected transcripts
                selected_expert_ids = list({t.expert_id for t in selected_transcripts})
                e_stmt = select(Expert).where(Expert.id.in_(selected_expert_ids))
                e_res = await self.db.execute(e_stmt)
                experts = list(e_res.scalars().all())

                logger.info(
                    f"Scoped analysis to {len(transcript_ids)} transcript(s) across {len(experts)} expert(s)",
                    extra={"operation": "run_full_analysis", "project_id": str(project_id)},
                )
            else:
                e_stmt = select(Expert).where(Expert.project_id == project_id)
                e_res = await self.db.execute(e_stmt)
                experts = list(e_res.scalars().all())

            if not experts:
                raise AnalysisError("No experts found for project. Please create experts and upload transcripts.")

            # Clear previous answers & evidence for a clean run
            await self.db.execute(delete(Answer).where(Answer.project_id == project_id))
            await self.db.execute(delete(Evidence).where(Evidence.project_id == project_id))
            await self.db.flush()

            # Pre-load utterances — filtered to selected transcripts if specified
            u_query = select(Utterance).join(Transcript).where(Transcript.project_id == project_id)
            if transcript_ids:
                u_query = u_query.where(Transcript.id.in_(transcript_ids))
            u_res = await self.db.execute(u_query)
            utterances = list(u_res.scalars().all())
            utterance_lookup = {str(u.id): u for u in utterances}

            # 3. For each Question x Expert: Extract Evidence & Generate Answer
            for q in questions:
                for exp in experts:
                    # Run evidence graph
                    ev_initial_state = {
                        "project_id": str(project_id),
                        "question_id": str(q.id),
                        "expert_id": str(exp.id),
                        "question_text": q.question_text,
                        "question_number": q.question_number,
                        "category": q.category,
                        "expert_name": exp.name,
                        "expert_role": exp.role,
                        "expert_market": exp.market,
                        "candidate_utterances": [],
                        "classified_evidence": [],
                        "evidence_ids": [],
                        "is_sufficient": False,
                        "error": None,
                    }

                    # We populate candidate utterance texts before graph execution if possible, or within node
                    # Retrieve candidates
                    ev_final_state = await evidence_graph.ainvoke(ev_initial_state)

                    # If candidate_utterances came from Qdrant without text, populate text from DB
                    classified_records = ev_final_state.get("classified_evidence", [])
                    if not classified_records and ev_final_state.get("candidate_utterances"):
                        # Re-run classification with full texts populated
                        candidates_with_text = []
                        for c in ev_final_state["candidate_utterances"]:
                            utt_obj = utterance_lookup.get(c["utterance_id"])
                            if utt_obj:
                                c_copy = dict(c)
                                c_copy["text"] = utt_obj.text
                                candidates_with_text.append(c_copy)
                        
                        ev_initial_state["candidate_utterances"] = candidates_with_text
                        from app.graphs.evidence_graph import classify_candidates_node
                        re_class = await classify_candidates_node(ev_initial_state)
                        classified_records = re_class.get("classified_evidence", [])

                    # Persist Evidence objects
                    created_evidence_objs: list[Evidence] = []
                    for item in classified_records:
                        u_obj = utterance_lookup.get(item["utterance_id"])
                        if u_obj:
                            ev = Evidence(
                                project_id=project_id,
                                question_id=q.id,
                                transcript_id=u_obj.transcript_id,
                                expert_id=exp.id,
                                utterance_id=u_obj.id,
                                quote=u_obj.text,  # Exact quote strictly from DB
                                topic=item.get("topic") or q.category,
                                relevance_score=item.get("relevance_score", 1.0),
                            )
                            self.db.add(ev)
                            created_evidence_objs.append(ev)

                    await self.db.flush()
                    for ev in created_evidence_objs:
                        await self.db.refresh(ev)

                    # Prepare evidence for answer graph
                    evidence_payload_for_answer = [
                        {
                            "id": str(ev.id),
                            "quote": ev.quote,
                            "topic": ev.topic,
                            "timestamp_start": utterance_lookup[str(ev.utterance_id)].timestamp_start if str(ev.utterance_id) in utterance_lookup else None,
                            "timestamp_end": utterance_lookup[str(ev.utterance_id)].timestamp_end if str(ev.utterance_id) in utterance_lookup else None,
                        }
                        for ev in created_evidence_objs
                    ]

                    # Run answer graph
                    ans_initial_state = {
                        "project_id": str(project_id),
                        "question_id": str(q.id),
                        "expert_id": str(exp.id),
                        "question_number": q.question_number,
                        "question_text": q.question_text,
                        "category": q.category,
                        "expert_name": exp.name,
                        "expert_role": exp.role,
                        "expert_market": exp.market,
                        "available_evidence": evidence_payload_for_answer,
                        "answer_text": None,
                        "validated_evidence_ids": [],
                        "is_valid": False,
                        "retry_count": 0,
                        "error": None,
                    }

                    ans_final_state = await answer_graph.ainvoke(ans_initial_state)

                    # Persist answer
                    answer_text = ans_final_state.get("answer_text") or "No answer could be generated from available evidence."
                    answer_obj = Answer(
                        project_id=project_id,
                        question_id=q.id,
                        expert_id=exp.id,
                        answer_text=answer_text,
                        status=AnalysisStatus.COMPLETED.value,
                    )
                    self.db.add(answer_obj)
                    await self.db.flush()
                    await self.db.refresh(answer_obj)

                    # Link validated evidence items
                    valid_eids = ans_final_state.get("validated_evidence_ids", [])
                    linked_evidence = [ev for ev in created_evidence_objs if str(ev.id) in valid_eids]
                    if not linked_evidence and created_evidence_objs:
                        linked_evidence = created_evidence_objs

                    answer_obj.evidence_items = linked_evidence
                    await self.db.flush()

            # 4. Run difference analysis for each question
            for q in questions:
                await self.difference_service.analyze_differences_for_question(project_id, q)

            # 5. Run project-wide insight generation
            await self.insight_service.generate_project_insights(project_id)

            project.status = ProjectStatus.COMPLETED.value
            await self.db.flush()

            # 6. Build and return full analysis response
            return await self.get_project_analysis(project_id)

        except Exception as e:
            project.status = ProjectStatus.FAILED.value
            await self.db.flush()
            logger.error(
                f"Full analysis failed: {e}",
                extra={"operation": "run_full_analysis", "project_id": str(project_id), "error": str(e)},
            )
            raise

    async def get_project_analysis(self, project_id: UUID) -> AnalysisResponse:
        """Get the current analysis state for all questions in a project."""
        p_stmt = select(Project).where(Project.id == project_id)
        p_res = await self.db.execute(p_stmt)
        project = p_res.scalar_one_or_none()
        if not project:
            raise ProjectNotFoundError(project_id)

        q_stmt = (
            select(ResearchQuestion)
            .where(ResearchQuestion.project_id == project_id)
            .order_by(ResearchQuestion.question_number.asc())
        )
        q_res = await self.db.execute(q_stmt)
        questions = list(q_res.scalars().all())

        question_responses = []
        for q in questions:
            a_stmt = (
                select(Answer)
                .where(Answer.project_id == project_id, Answer.question_id == q.id)
                .options(
                    selectinload(Answer.evidence_items).selectinload(Evidence.expert),
                    selectinload(Answer.evidence_items).selectinload(Evidence.transcript),
                    selectinload(Answer.evidence_items).selectinload(Evidence.utterance),
                )
            )
            a_res = await self.db.execute(a_stmt)
            answers = list(a_res.scalars().all())

            answer_responses = []
            for ans in answers:
                evidence_responses = [
                    self.evidence_service.format_evidence_response(ev)
                    for ev in ans.evidence_items
                ]
                answer_responses.append(
                    AnswerResponse(
                        id=ans.id,
                        project_id=ans.project_id,
                        question_id=ans.question_id,
                        expert_id=ans.expert_id,
                        answer_text=ans.answer_text,
                        status=ans.status,
                        evidence=evidence_responses,
                        created_at=ans.created_at,
                        updated_at=ans.updated_at,
                    )
                )

            question_responses.append(
                AnalysisQuestionResponse(
                    question_id=q.id,
                    question_number=q.question_number,
                    question_text=q.question_text,
                    answers=answer_responses,
                )
            )

        return AnalysisResponse(
            project_id=project_id,
            status=project.status,
            questions=question_responses,
        )

    async def get_question_analysis(self, project_id: UUID, question_id: UUID) -> AnalysisQuestionResponse:
        """Get analysis results for a specific research question."""
        q_stmt = select(ResearchQuestion).where(
            ResearchQuestion.id == question_id,
            ResearchQuestion.project_id == project_id,
        )
        q_res = await self.db.execute(q_stmt)
        question = q_res.scalar_one_or_none()
        if not question:
            raise AnalysisError(f"Question {question_id} not found in project {project_id}")

        a_stmt = (
            select(Answer)
            .where(Answer.project_id == project_id, Answer.question_id == question_id)
            .options(
                selectinload(Answer.evidence_items).selectinload(Evidence.expert),
                selectinload(Answer.evidence_items).selectinload(Evidence.transcript),
                selectinload(Answer.evidence_items).selectinload(Evidence.utterance),
            )
        )
        a_res = await self.db.execute(a_stmt)
        answers = list(a_res.scalars().all())

        answer_responses = []
        for ans in answers:
            evidence_responses = [
                self.evidence_service.format_evidence_response(ev)
                for ev in ans.evidence_items
            ]
            answer_responses.append(
                AnswerResponse(
                    id=ans.id,
                    project_id=ans.project_id,
                    question_id=ans.question_id,
                    expert_id=ans.expert_id,
                    answer_text=ans.answer_text,
                    status=ans.status,
                    evidence=evidence_responses,
                    created_at=ans.created_at,
                    updated_at=ans.updated_at,
                )
            )

        return AnalysisQuestionResponse(
            question_id=question.id,
            question_number=question.question_number,
            question_text=question.question_text,
            answers=answer_responses,
        )
