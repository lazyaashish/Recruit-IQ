"""
Pydantic request/response schemas for all API endpoints.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ── Auth ─────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ── Resume ───────────────────────────────────────────────────────────────────

class ResumeResponse(BaseModel):
    id: int
    filename: str
    skills: list[str]
    contact_info: dict
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Job Description ───────────────────────────────────────────────────────────

class JobDescriptionCreate(BaseModel):
    title: str
    company: Optional[str] = None
    raw_text: str = Field(min_length=50)


class JobDescriptionResponse(BaseModel):
    id: int
    title: str
    company: Optional[str]
    required_skills: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Analysis ─────────────────────────────────────────────────────────────────

class AnalysisRequest(BaseModel):
    resume_id: int
    job_description_id: int


class SkillOverlap(BaseModel):
    matching_skills: list[str]
    missing_skills: list[str]
    extra_skills: list[str]


class ScoreBreakdown(BaseModel):
    overall_score: float = Field(description="0–100 composite score")
    semantic_score: float = Field(description="Semantic similarity (embeddings)")
    keyword_score: float = Field(description="Keyword coverage")
    skill_overlap_score: float = Field(description="Skill set overlap")
    confidence: float = Field(description="Score confidence 0–100")
    grade: str


class RoadmapMilestone(BaseModel):
    skill: str
    level: str
    estimated_weeks: int
    resources: list[dict]


class Roadmap(BaseModel):
    role_target: str
    estimated_total_weeks: int
    phases: list[dict]
    milestones: list[RoadmapMilestone]
    quick_wins: list[str]


class InterviewQuestion(BaseModel):
    question: str
    skill: str
    type: str
    note: str


class InterviewPack(BaseModel):
    role: str
    technical_questions: list[InterviewQuestion]
    behavioral_questions: list[str]
    system_design_questions: list[str]
    total_count: int


class AnalysisResponse(BaseModel):
    id: int
    resume_id: int
    job_description_id: int
    score: ScoreBreakdown
    skill_overlap: SkillOverlap
    keyword_gaps: list[str]
    keyword_hits: list[str]
    suggestions: list[str]
    roadmap: Roadmap
    interview_pack: InterviewPack
    created_at: datetime


class AnalysisSummary(BaseModel):
    id: int
    job_title: str
    company: Optional[str]
    overall_score: float
    grade: str
    created_at: datetime


class DashboardResponse(BaseModel):
    total_analyses: int
    average_score: float
    best_match: Optional[AnalysisSummary]
    recent_analyses: list[AnalysisSummary]
    top_missing_skills: list[str]
    top_matching_skills: list[str]
