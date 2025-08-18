from sqlmodel import Session, select
from .db import get_session
from .models.user import User
from .security import get_password_hash
from .config import settings


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
