"""
Resume upload and management endpoints.
"""
import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.schemas import ResumeResponse
from app.core.database import get_db
from app.models.analysis import Resume
from app.models.user import User
from app.services.parser import DocumentParser, ResumeParser
from app.services.skill_extractor import SkillExtractor

router = APIRouter(prefix="/resumes", tags=["resumes"])

_doc_parser = DocumentParser()
_resume_parser = ResumeParser()
_skill_extractor = SkillExtractor()

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    content = await file.read()
    if len(content) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds 5 MB limit")

    raw_text = _doc_parser.parse_bytes(content, file.filename or "resume.txt")
    if not raw_text.strip():
        raise HTTPException(status_code=422, detail="Could not extract text from file")

    parsed = _resume_parser.parse(raw_text)
    skills = _skill_extractor.extract(raw_text)

    resume = Resume(
        user_id=current_user.id,
        filename=file.filename or "resume.txt",
        raw_text=raw_text,
        parsed_sections=json.dumps(parsed.to_dict()),
        skills=json.dumps(skills),
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return ResumeResponse(
        id=resume.id,
        filename=resume.filename,
        skills=skills,
        contact_info=parsed.contact_info,
        created_at=resume.created_at,
    )


@router.get("/", response_model=list[ResumeResponse])
def list_resumes(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).all()
    results = []
    for r in resumes:
        sections = r.get_parsed_sections()
        contact = sections.get("contact_info", {})
        results.append(ResumeResponse(
            id=r.id,
            filename=r.filename,
            skills=r.get_skills(),
            contact_info=contact,
            created_at=r.created_at,
        ))
    return results


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    resume = db.query(Resume).filter(
        Resume.id == resume_id, Resume.user_id == current_user.id
    ).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    db.delete(resume)
    db.commit()
