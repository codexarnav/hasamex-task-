"""Transcript schemas."""
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class TranscriptResponse(BaseModel):
    id: UUID
    project_id: UUID
    expert_id: UUID
    file_name: str
    status: str
    duration: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TranscriptDetailResponse(TranscriptResponse):
    utterance_count: int = 0


class TranscriptsListResponse(BaseModel):
    transcripts: list[TranscriptResponse]
    total: int


class UtteranceResponse(BaseModel):
    id: UUID
    transcript_id: UUID
    expert_id: UUID
    speaker: str
    text: str
    timestamp_start: str | None
    timestamp_end: str | None
    sequence: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TranscriptUtterancesResponse(BaseModel):
    transcript_id: UUID
    utterances: list[UtteranceResponse]
    total: int

