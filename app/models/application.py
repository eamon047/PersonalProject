from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint
from typing import Optional, Dict, Any
from enum import Enum


class ApplicationStatus(str, Enum):
    applied = "applied"
    cancelled_by_candidate = "cancelled_by_candidate"


class Application(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_application_user_job"),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    job_id: int = Field(foreign_key="job.id")
    status: ApplicationStatus = Field(default=ApplicationStatus.applied)
    application_note: Optional[str] = None
    
    # 关系定义
    user: Optional["User"] = Relationship(back_populates="applications")
    job: Optional["Job"] = Relationship(back_populates="applications")
