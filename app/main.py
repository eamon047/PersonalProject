from fastapi import FastAPI
from contextlib import asynccontextmanager

from .db import create_db_and_tables
from .admin_init import create_admin_user
from .routers import auth, admin, profile, companies, jobs, applications

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    create_db_and_tables()
    create_admin_user()
    yield
    # 关闭时执行（如果需要的话）

app = FastAPI(title="Job Platform MVP", lifespan=lifespan)

# 路由挂载
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(profile.router, prefix="/profile", tags=["profile"])
app.include_router(companies.router, prefix="/companies", tags=["companies"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(applications.router, prefix="/applications", tags=["applications"])
