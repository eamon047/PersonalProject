from pydantic import BaseModel, Field
from typing import Optional


class CompanyCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    website: Optional[str] = Field(default=None, max_length=500)


class CompanyResponse(BaseModel):
    id: int
    owner_id: int
    name: str
    website: Optional[str] = None
