from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..db import get_session
from ..deps import get_current_user
from ..models.company import Company
from ..models.user import User
from ..models.job import Job
from ..models.application import Application
from ..schemas.company import CompanyCreateRequest, CompanyResponse

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CompanyResponse)
def create_company(
    payload: CompanyCreateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    exists = session.exec(select(Company).where(Company.owner_id == current_user.id)).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="the user already has a company")

    company = Company(owner_id=current_user.id, name=payload.name, website=payload.website)
    session.add(company)
    session.commit()
    session.refresh(company)

    return CompanyResponse(id=company.id, owner_id=company.owner_id, name=company.name)


@router.get("/me")
def get_my_company(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    company = session.exec(select(Company).where(Company.owner_id == current_user.id)).first()
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="company not found")

    # 简单统计：该公司下的职位数量与总投递数量
    job_ids = [j for j in session.exec(select(Job.id).where(Job.company_id == company.id)).all()]
    jobs_count = len(job_ids)
    if job_ids:
        applications_count = len(
            session.exec(select(Application.id).where(Application.job_id.in_(job_ids))).all()
        )
    else:
        applications_count = 0

    return {
        "company": CompanyResponse(id=company.id, owner_id=company.owner_id, name=company.name, website=company.website),
        "stats": {"jobs": jobs_count, "applications": applications_count},
    }
