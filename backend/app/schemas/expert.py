"""Expert schemas."""
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class ExpertCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    role: str | None = None
    market: str | None = None
    organization: str | None = None


class ExpertResponse(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    role: str | None
    market: str | None
    organization: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ExpertBrief(BaseModel):
    id: UUID
    name: str
    role: str | None = None
    market: str | None = None

    model_config = {"from_attributes": True}


class ExpertsListResponse(BaseModel):
    experts: list[ExpertResponse]
    total: int
