from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..db import get_session
from ..deps import get_current_user
from ..models.user import User
from ..models.job import Job
from ..models.application import Application, ApplicationStatus
from ..models.candidate_profile import CandidateProfile
from ..schemas.application import ApplicationCreateRequest, ApplicationResponse

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ApplicationResponse)
def create_application(
    payload: ApplicationCreateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    # 检查职位是否存在
    job = session.get(Job, payload.job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="职位不存在")

    # 检查是否已投递过该职位
    existing = session.exec(
        select(Application).where(
            Application.user_id == current_user.id,
            Application.job_id == payload.job_id
        )
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="已投递过该职位")

    # 获取候选人资料（用于快照）
    profile = session.exec(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    ).first()
    if profile is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请先完善个人资料")

    # 创建投递记录
    application = Application(
        user_id=current_user.id,
        job_id=payload.job_id,
        status=ApplicationStatus.applied,
        application_note=payload.application_note,
    )
    session.add(application)
    session.commit()
    session.refresh(application)

    return ApplicationResponse(
        id=application.id,
        user_id=application.user_id,
        job_id=application.job_id,
        status=application.status,
        application_note=application.application_note,
    )


@router.get("/me", response_model=List[ApplicationResponse])
def get_my_applications(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    applications = session.exec(
        select(Application).where(Application.user_id == current_user.id)
    ).all()
    
    return [
        ApplicationResponse(
            id=app.id,
            user_id=app.user_id,
            job_id=app.job_id,
            status=app.status,
            application_note=app.application_note,
        )
        for app in applications
    ]


@router.patch("/{application_id}/cancel")
def cancel_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    application = session.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="投递记录不存在")

    # 权限：仅本人可取消
    if application.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权操作该投递")

    # 检查状态：已取消的不可再次取消
    if application.status == ApplicationStatus.cancelled_by_candidate:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该投递已取消")

    application.status = ApplicationStatus.cancelled_by_candidate
    session.add(application)
    session.commit()
    session.refresh(application)

    return {"status": application.status}
