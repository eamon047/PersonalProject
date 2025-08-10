from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List


class Company(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id", unique=True)
    name: str
    
    # 关系定义
    owner: Optional["User"] = Relationship(back_populates="company")
    jobs: List["Job"] = Relationship(back_populates="company")
