from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..deps import require_admin
from ..db import get_session
from ..models.user import User
from ..models.company import Company
from ..models.job import Job
from ..models.application import Application
from ..models.candidate_profile import CandidateProfile
from ..schemas.user import UserResponse
from ..schemas.company import CompanyResponse
from ..schemas.job import JobResponse
from ..schemas.application import ApplicationResponse

router = APIRouter()


@router.get("/ping")
def admin_ping(user: User = Depends(require_admin)):
    """管理员权限验证端点"""
    return {"message": "Admin access confirmed", "user_id": user.id}


@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    """获取所有用户列表"""
    users = session.exec(select(User)).all()
    
    return [
        UserResponse(
            id=u.id,
            email=u.email,
            is_admin=u.is_admin,
        )
        for u in users
    ]


@router.get("/companies", response_model=List[CompanyResponse])
def get_all_companies(
    user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    """获取所有公司列表"""
    companies = session.exec(select(Company)).all()
    
    return [
        CompanyResponse(
            id=c.id,
            owner_id=c.owner_id,
            name=c.name,
        )
        for c in companies
    ]


@router.get("/jobs", response_model=List[JobResponse])
def get_all_jobs(
    user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    """获取所有职位列表"""
    jobs = session.exec(select(Job)).all()
    
    return [
        JobResponse(
            id=j.id,
            company_id=j.company_id,
            title=j.title,
            position=j.position,
            based_in_code=j.based_in_code,
            description=j.description,
            salary=j.salary,
        )
        for j in jobs
    ]


@router.get("/applications", response_model=List[ApplicationResponse])
def get_all_applications(
    user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    """获取所有投递列表"""
    applications = session.exec(select(Application)).all()
    
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


@router.get("/profiles")
def get_all_profiles(
    user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    """获取所有候选人资料列表"""
    profiles = session.exec(select(CandidateProfile)).all()
    
    result = []
    for profile in profiles:
        # 获取对应的用户邮箱信息
        user = session.get(User, profile.user_id)
        
        result.append({
            "user_id": profile.user_id,
            "user_email": user.email if user else "未知",
            "full_name": profile.full_name,
            "age": profile.age,
            "gender": profile.gender,
            "phone": profile.phone,
            "intro": profile.intro,
        })
    
    return result


@router.get("/stats")
def get_system_stats(
    user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    """获取系统统计信息"""
    users = session.exec(select(User)).all()
    companies = session.exec(select(Company)).all()
    jobs = session.exec(select(Job)).all()
    applications = session.exec(select(Application)).all()
    profiles = session.exec(select(CandidateProfile)).all()
    
    return {
        "total_users": len(users),
        "total_companies": len(companies),
        "total_jobs": len(jobs),
        "total_applications": len(applications),
        "total_profiles": len(profiles),
    }
