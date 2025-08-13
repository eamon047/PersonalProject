from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..db import get_session
from ..deps import get_current_user
from ..models.candidate_profile import CandidateProfile
from ..models.user import User
from ..schemas.profile import ProfileResponse, ProfileUpdateRequest

router = APIRouter()


@router.get("/me", response_model=ProfileResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    profile = session.exec(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    ).first()
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到个人资料")
    return ProfileResponse(
        user_id=profile.user_id,
        full_name=profile.full_name,
        age=profile.age,
        gender=profile.gender,
        phone=profile.phone,
        intro=profile.intro,
    )


@router.put("/", response_model=ProfileResponse)
def upsert_profile(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    profile = session.exec(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    ).first()

    if profile is None:
        profile = CandidateProfile(
            user_id=current_user.id,
            full_name=payload.full_name,
            age=payload.age,
            gender=payload.gender,
            phone=payload.phone,
            intro=payload.intro,
        )
        session.add(profile)
    else:
        profile.full_name = payload.full_name
        profile.age = payload.age
        profile.gender = payload.gender
        profile.phone = payload.phone
        profile.intro = payload.intro

    session.commit()
    session.refresh(profile)

    return ProfileResponse(
        user_id=profile.user_id,
        full_name=profile.full_name,
        age=profile.age,
        gender=profile.gender,
        phone=profile.phone,
        intro=profile.intro,
    )
