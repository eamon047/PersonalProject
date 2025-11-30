from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..db import get_session
from ..models.user import User
from ..security import get_password_hash, verify_password, create_access_token
from ..schemas.auth import RegisterRequest, LoginRequest, TokenResponse

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, session: Session = Depends(get_session)):
    # 邮箱唯一性检查
    exists = session.exec(select(User).where(User.email == payload.email)).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    
    # 创建用户
    user = User(email=payload.email, password_hash=get_password_hash(payload.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"id": user.id, "email": user.email}

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == payload.email)).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Worng email or password")
    
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)
