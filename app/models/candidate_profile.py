from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from enum import Enum


class Gender(str, Enum):
    male = "male"
    female = "female"


class CandidateProfile(SQLModel, table=True):
    user_id: int = Field(primary_key=True, foreign_key="user.id")
    full_name: str = Field(max_length=80)
    age: int = Field(ge=18, le=80)
    gender: Gender
    phone: Optional[str] = None
    intro: Optional[str] = Field(max_length=1000, default=None)
    
    # 关系定义
    user: Optional["User"] = Relationship(back_populates="profile")
