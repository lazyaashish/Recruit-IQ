"""
Job description management endpoints.
"""
import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.schemas import JobDescriptionCreate, JobDescriptionResponse
from app.core.database import get_db
from app.models.analysis import JobDescription
from app.models.user import User
from app.services.parser import JobDescriptionParser
from app.services.skill_extractor import SkillExtractor

router = APIRouter(prefix="/jobs", tags=["jobs"])

_jd_parser = JobDescriptionParser()
_skill_extractor = SkillExtractor()


@router.post("/", response_model=JobDescriptionResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: JobDescriptionCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    parsed = _jd_parser.parse(payload.raw_text)
    skills = _skill_extractor.extract(payload.raw_text)

    jd = JobDescription(
        user_id=current_user.id,
        title=payload.title or parsed.title,
        company=payload.company or parsed.company or None,
        raw_text=payload.raw_text,
        required_skills=json.dumps(skills),
    )
    db.add(jd)
    db.commit()
    db.refresh(jd)

    return JobDescriptionResponse(
        id=jd.id,
        title=jd.title,
        company=jd.company,
        required_skills=skills,
        created_at=jd.created_at,
    )


@router.get("/", response_model=list[JobDescriptionResponse])
def list_jobs(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    jobs = db.query(JobDescription).filter(
        JobDescription.user_id == current_user.id
    ).order_by(JobDescription.created_at.desc()).all()
    return [
        JobDescriptionResponse(
            id=j.id,
            title=j.title,
            company=j.company,
            required_skills=j.get_required_skills(),
            created_at=j.created_at,
        )
        for j in jobs
    ]


@router.get("/{job_id}", response_model=JobDescriptionResponse)
def get_job(
    job_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    jd = db.query(JobDescription).filter(
        JobDescription.id == job_id, JobDescription.user_id == current_user.id
    ).first()
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")
    return JobDescriptionResponse(
        id=jd.id,
        title=jd.title,
        company=jd.company,
        required_skills=jd.get_required_skills(),
        created_at=jd.created_at,
    )


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    jd = db.query(JobDescription).filter(
        JobDescription.id == job_id, JobDescription.user_id == current_user.id
    ).first()
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")
    db.delete(jd)
    db.commit()
