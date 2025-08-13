from pydantic import BaseModel
from typing import Optional

from ..models.application import ApplicationStatus


class ApplicationCreateRequest(BaseModel):
    job_id: int
    application_note: Optional[str] = None


class ApplicationResponse(BaseModel):
    id: int
    user_id: int
    job_id: int
    status: ApplicationStatus
    application_note: Optional[str] = None
