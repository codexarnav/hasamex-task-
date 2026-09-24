"""Transcript management and utterance ingestion API endpoints."""
from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.transcript import (
    TranscriptResponse,
    TranscriptDetailResponse,
    TranscriptsListResponse,
    TranscriptUtterancesResponse,
    UtteranceResponse,
)
from app.services.transcript_service import TranscriptService

router = APIRouter(tags=["Transcripts"])


@router.post("/projects/{project_id}/transcripts", response_model=TranscriptResponse, status_code=status.HTTP_201_CREATED)
async def upload_transcript(
    project_id: UUID,
    expert_id: UUID = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload an expert interview transcript, parse utterances with timestamps, embed, and index in Qdrant."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    service = TranscriptService(db)
    transcript = await service.process_transcript(
        project_id=project_id,
        expert_id=expert_id,
        filename=file.filename,
        content=content,
    )
    return transcript


@router.get("/projects/{project_id}/transcripts", response_model=TranscriptsListResponse)
async def list_transcripts(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """List all transcripts uploaded for a project."""
    service = TranscriptService(db)
    transcripts = await service.list_transcripts(project_id)
    return TranscriptsListResponse(
        transcripts=[TranscriptResponse.model_validate(t) for t in transcripts],
        total=len(transcripts),
    )


@router.get("/transcripts/{transcript_id}", response_model=TranscriptDetailResponse)
async def get_transcript_detail(
    transcript_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get detailed transcript information including utterance count."""
    service = TranscriptService(db)
    transcript = await service.get_transcript(transcript_id)
    count = await service.get_utterance_count(transcript_id)
    return TranscriptDetailResponse(
        id=transcript.id,
        project_id=transcript.project_id,
        expert_id=transcript.expert_id,
        file_name=transcript.file_name,
        status=transcript.status,
        duration=transcript.duration,
        created_at=transcript.created_at,
        updated_at=transcript.updated_at,
        utterance_count=count,
    )


@router.get("/transcripts/{transcript_id}/utterances", response_model=TranscriptUtterancesResponse)
async def get_transcript_utterances(
    transcript_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get all timestamped utterances for a transcript."""
    service = TranscriptService(db)
    await service.get_transcript(transcript_id)
    utterances = await service.get_transcript_utterances(transcript_id)
    return TranscriptUtterancesResponse(
        transcript_id=transcript_id,
        utterances=[UtteranceResponse.model_validate(u) for u in utterances],
        total=len(utterances),
    )


@router.delete("/transcripts/{transcript_id}", status_code=status.HTTP_204_NO_CONTENT)
@router.delete("/projects/{project_id}/transcripts/{transcript_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transcript(
    transcript_id: UUID,
    project_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Delete a transcript, its utterances, and indexed vectors."""
    service = TranscriptService(db)
    await service.delete_transcript(transcript_id)
    return None


