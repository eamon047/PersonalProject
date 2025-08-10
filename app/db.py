from sqlmodel import SQLModel, create_engine, Session
from .config import settings

# 创建数据库引擎
engine = create_engine(
    settings.database_url,
    echo=settings.app_env == "dev",  # 开发环境显示SQL语句
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)


def create_db_and_tables():
    """创建数据库和所有表"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """获取数据库会话"""
    with Session(engine) as session:
        yield session
