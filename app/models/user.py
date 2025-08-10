from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    
    # 关系定义
    company: Optional["Company"] = Relationship(back_populates="owner")
    profile: Optional["CandidateProfile"] = Relationship(back_populates="user")
    applications: List["Application"] = Relationship(back_populates="user")
