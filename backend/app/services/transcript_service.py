"""Transcript upload, parsing, utterance persistence, and vector indexing service."""
import io
from pathlib import Path
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.transcript import Transcript
from app.models.expert import Expert
from app.models.utterance import Utterance
from app.models.project import Project
from app.storage.local import local_storage
from app.parsers.transcript_parser import parse_transcript
from app.parsers.pdf_extractor import extract_pdf_text
from app.retrieval.embeddings import get_embedding_service
from app.retrieval.qdrant import get_qdrant_repository
from app.core.enums import TranscriptStatus
from app.core.exceptions import ProjectNotFoundError, ExpertNotFoundError, TranscriptNotFoundError, ParsingError
from app.core.logging import get_logger

logger = get_logger("services.transcript")


class TranscriptService:
    """Service handling transcript upload, utterance parsing, and Qdrant indexing."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_transcript(
        self,
        project_id: UUID,
        expert_id: UUID,
        filename: str,
        content: bytes,
    ) -> Transcript:
        """Process an uploaded transcript: parse utterances, persist to DB, embed, and index in Qdrant."""
        # 1. Validate project & expert
        p_stmt = select(Project).where(Project.id == project_id)
        p_res = await self.db.execute(p_stmt)
        if not p_res.scalar_one_or_none():
            raise ProjectNotFoundError(project_id)

        e_stmt = select(Expert).where(Expert.id == expert_id, Expert.project_id == project_id)
        e_res = await self.db.execute(e_stmt)
        expert = e_res.scalar_one_or_none()
        if not expert:
            raise ExpertNotFoundError(expert_id)

        # 2. Save file
        rel_path = local_storage.save(project_id, filename, content)

        # 3. Create Transcript record
        transcript = Transcript(
            project_id=project_id,
            expert_id=expert_id,
            file_name=filename,
            file_path=rel_path,
            status=TranscriptStatus.PARSING.value,
        )
        self.db.add(transcript)
        await self.db.flush()
        await self.db.refresh(transcript)

        try:
            # 4. Parse text into structured utterances
            text = _extract_text_from_content(content, filename)
            parsed = parse_transcript(text)

            # 5. Persist Utterances in PostgreSQL
            utterance_objs: list[Utterance] = []
            for u in parsed.utterances:
                utt = Utterance(
                    transcript_id=transcript.id,
                    expert_id=expert_id,
                    speaker=u.speaker,
                    text=u.text,
                    timestamp_start=u.timestamp_start,
                    timestamp_end=u.timestamp_end,
                    sequence=u.sequence,
                )
                self.db.add(utt)
                utterance_objs.append(utt)

            await self.db.flush()

            # Refresh to ensure UUIDs are populated
            for utt in utterance_objs:
                await self.db.refresh(utt)

            transcript.status = TranscriptStatus.EMBEDDING.value
            await self.db.flush()

            # 6. Generate embeddings and index in Qdrant
            embedding_service = get_embedding_service()
            qdrant_repo = get_qdrant_repository()

            # Ensure Qdrant collection is ready
            await qdrant_repo.init_collection()

            texts_to_embed = [u.text for u in utterance_objs]
            vectors = await embedding_service.embed_batch(texts_to_embed)

            qdrant_records = []
            for utt, vec in zip(utterance_objs, vectors):
                qdrant_records.append({
                    "utterance_id": utt.id,
                    "vector": vec,
                    "speaker": utt.speaker,
                    "market": expert.market,
                    "timestamp_start": utt.timestamp_start,
                    "timestamp_end": utt.timestamp_end,
                    "text": utt.text,
                })

            await qdrant_repo.upsert_utterances(
                project_id=project_id,
                transcript_id=transcript.id,
                expert_id=expert_id,
                utterance_records=qdrant_records,
            )

            transcript.status = TranscriptStatus.READY.value
            await self.db.flush()

            logger.info(
                f"Transcript {transcript.id} ready with {len(utterance_objs)} utterances indexed",
                extra={"operation": "process_transcript", "project_id": str(project_id)},
            )
            return transcript

        except Exception as e:
            transcript.status = TranscriptStatus.FAILED.value
            await self.db.flush()
            logger.error(
                f"Transcript processing failed: {e}",
                extra={"operation": "process_transcript", "error": str(e)},
            )
            raise

    async def get_transcript(self, transcript_id: UUID) -> Transcript:
        """Get transcript by ID."""
        stmt = select(Transcript).where(Transcript.id == transcript_id)
        res = await self.db.execute(stmt)
        transcript = res.scalar_one_or_none()
        if not transcript:
            raise TranscriptNotFoundError(transcript_id)
        return transcript

    async def list_transcripts(self, project_id: UUID) -> list[Transcript]:
        """List all transcripts for a project."""
        stmt = (
            select(Transcript)
            .where(Transcript.project_id == project_id)
            .order_by(Transcript.created_at.desc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_utterance_count(self, transcript_id: UUID) -> int:
        """Get total count of utterances for a transcript."""
        stmt = select(func.count(Utterance.id)).where(Utterance.transcript_id == transcript_id)
        res = await self.db.execute(stmt)
        return res.scalar() or 0

    async def get_transcript_utterances(self, transcript_id: UUID) -> list[Utterance]:
        """Get all utterances for a transcript ordered by sequence."""
        stmt = (
            select(Utterance)
            .where(Utterance.transcript_id == transcript_id)
            .order_by(Utterance.sequence.asc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def delete_transcript(self, transcript_id: UUID) -> None:
        """Delete a transcript, its utterances, vector embeddings in Qdrant, and raw stored file."""
        transcript = await self.get_transcript(transcript_id)

        # 1. Delete vector embeddings in Qdrant
        try:
            qdrant_repo = get_qdrant_repository()
            await qdrant_repo.delete_transcript_vectors(transcript.project_id, transcript_id)
        except Exception as e:
            logger.warning(f"Could not delete Qdrant vectors for transcript {transcript_id}: {e}")

        # 2. Delete stored file on disk
        if transcript.file_path:
            try:
                local_storage.delete(transcript.file_path)
            except Exception as e:
                logger.warning(f"Could not delete local file for transcript {transcript_id}: {e}")

        # 3. Delete transcript record from DB (foreign keys will cascade to Utterances & Evidence)
        await self.db.delete(transcript)
        await self.db.flush()

        logger.info(
            f"Deleted transcript {transcript_id}",
            extra={"operation": "delete_transcript", "project_id": str(transcript.project_id)},
        )


def _extract_text_from_content(content: bytes, filename: str) -> str:
    """Extract text from transcript file content.

    Supports PDF files (via multi-tier PyMuPDF/OCR engine) and text files (UTF-8/Latin-1).
    """
    suffix = Path(filename).suffix.lower()

    if suffix == ".pdf":
        return extract_pdf_text(content)
    else:
        # Text-based formats (.txt, .md, .csv, etc.)
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                return content.decode("latin-1")
            except UnicodeDecodeError:
                return content.decode("utf-8", errors="replace")

