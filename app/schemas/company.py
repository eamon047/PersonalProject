from pydantic import BaseModel, Field


class CompanyCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class CompanyResponse(BaseModel):
    id: int
    owner_id: int
    name: str
