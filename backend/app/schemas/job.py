from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class JobResponse(BaseModel):
    id: str
    project_id: str
    status: str
    progress: int
    current_step: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True
