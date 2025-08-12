from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..deps import require_admin
from ..db import get_session
from ..models.user import User

router = APIRouter()

@router.get("/ping")
def admin_ping(user: User = Depends(require_admin)):
    """管理员权限验证端点"""
    return {"message": "Admin access confirmed", "user_id": user.id}
