"""Guide schemas."""
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class GuideResponse(BaseModel):
    id: UUID
    project_id: UUID
    source_file: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
