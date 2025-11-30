from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..db import get_session
from ..deps import get_current_user
from ..models.user import User
from ..models.company import Company
from ..models.job import Job, Position
from ..schemas.job import JobCreateRequest, JobUpdateRequest, JobResponse

router = APIRouter()


def _get_user_company(session: Session, user_id: int) -> Optional[Company]:
    return session.exec(select(Company).where(Company.owner_id == user_id)).first()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=JobResponse)
def create_job(
    payload: JobCreateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    company = _get_user_company(session, current_user.id)
    if company is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="no company associated with the user")

    job = Job(
        company_id=company.id,
        title=payload.title,
        position=payload.position,
        based_in_code=payload.based_in_code,
        description=payload.description,
        salary=payload.salary,
    )
    session.add(job)
    session.commit()
    session.refresh(job)

    return JobResponse(
        id=job.id,
        company_id=job.company_id,
        title=job.title,
        position=job.position,
        based_in_code=job.based_in_code,
        description=job.description,
        salary=job.salary,
    )


@router.get("/", response_model=List[JobResponse])
def list_jobs(
    position: Optional[Position] = None,
    based_in_code: Optional[int] = None,
    salary_min: Optional[int] = None,
    salary_max: Optional[int] = None,
    session: Session = Depends(get_session),
):
    stmt = select(Job)
    if position is not None:
        stmt = stmt.where(Job.position == position)
    if based_in_code is not None:
        stmt = stmt.where(Job.based_in_code == based_in_code)
    if salary_min is not None:
        stmt = stmt.where(Job.salary >= salary_min)
    if salary_max is not None:
        stmt = stmt.where(Job.salary <= salary_max)

    jobs = session.exec(stmt).all()
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


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, session: Session = Depends(get_session)):
    job = session.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="occupation not found")
    return JobResponse(
        id=job.id,
        company_id=job.company_id,
        title=job.title,
        position=job.position,
        based_in_code=job.based_in_code,
        description=job.description,
        salary=job.salary,
    )


@router.patch("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    payload: JobUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    job = session.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="occupation not found")

    # 权限：仅职位所属公司的拥有者可编辑
    company = _get_user_company(session, current_user.id)
    if company is None or company.id != job.company_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="no permission to edit this job")

    if payload.title is not None:
        job.title = payload.title
    if payload.position is not None:
        job.position = payload.position
    if payload.based_in_code is not None:
        job.based_in_code = payload.based_in_code
    if payload.description is not None:
        job.description = payload.description
    if payload.salary is not None:
        job.salary = payload.salary

    session.add(job)
    session.commit()
    session.refresh(job)

    return JobResponse(
        id=job.id,
        company_id=job.company_id,
        title=job.title,
        position=job.position,
        based_in_code=job.based_in_code,
        description=job.description,
        salary=job.salary,
    )
