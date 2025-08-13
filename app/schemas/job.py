from pydantic import BaseModel, Field
from typing import Optional

from ..models.job import Position


class JobCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    position: Position
    based_in_code: int = Field(ge=0, le=1)
    description: str = Field(min_length=1, max_length=10000)
    salary: int = Field(ge=0)


class JobUpdateRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=120)
    position: Optional[Position] = None
    based_in_code: Optional[int] = Field(default=None, ge=0, le=1)
    description: Optional[str] = Field(default=None, min_length=1, max_length=10000)
    salary: Optional[int] = Field(default=None, ge=0)


class JobResponse(BaseModel):
    id: int
    company_id: int
    title: str
    position: Position
    based_in_code: int
    description: str
    salary: int
