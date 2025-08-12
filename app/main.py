from fastapi import FastAPI
from .db import create_db_and_tables
from .routers import auth

app = FastAPI(title="Job Platform MVP")

@app.on_event("startup")
def on_startup():
    # 启动时确保数据库与表存在
    create_db_and_tables()

@app.get("/health")
def health_check():
    return {"status": "ok"}

# 路由
app.include_router(auth.router, prefix="/auth", tags=["auth"])
