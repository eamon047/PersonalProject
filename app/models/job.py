from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from enum import Enum


class Position(str, Enum):
    frontend = "frontend"
    backend = "backend"
    fullstack = "fullstack"


class Job(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="company.id")
    title: str = Field(max_length=120)
    position: Position
    based_in_code: int = Field(description="0=tokyo, 1=osaka")
    # 整数代替文字(枚举类型的一种实现方式)：节省空间、查询快（数字比字符串好比对）、方便统一管理
    description: str = Field(max_length=10000)
    salary: int = Field(ge=0, description="万日元")
    
    # 关系定义
    company: Optional["Company"] = Relationship(back_populates="jobs")
    applications: List["Application"] = Relationship(back_populates="job")
