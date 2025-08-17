from fastapi import FastAPI
from sqlmodel import Session, select
from .db import create_db_and_tables, get_session
from .routers import auth, admin
from .models.user import User
from .security import get_password_hash
from .config import settings
from .routers import profile
from .routers import companies
from .routers import jobs
from .routers import applications
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    create_db_and_tables()
    create_admin_user()
    yield
    # 关闭时执行（如果需要的话）

app = FastAPI(title="Job Platform MVP", lifespan=lifespan)

def create_admin_user():
    """创建种子管理员用户"""
    with next(get_session()) as session:
        # 检查管理员是否已存在
        admin_user = session.exec(
            select(User).where(User.email == settings.admin_email)
        ).first()
        
        if admin_user is None:
            # 创建管理员用户
            admin_user = User(
                email=settings.admin_email,
                password_hash=get_password_hash(settings.admin_password),
                is_admin=True
            )
            session.add(admin_user)
            session.commit()
            print(f"✅ 管理员用户已创建: {settings.admin_email}")
        else:
            print(f"✅ 管理员用户已存在: {settings.admin_email}")

@app.get("/health")
def health_check():
    return {"status": "ok"}

# 路由
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(profile.router, prefix="/profile", tags=["profile"])
app.include_router(companies.router, prefix="/companies", tags=["companies"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(applications.router, prefix="/applications", tags=["applications"])
