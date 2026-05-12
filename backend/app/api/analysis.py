"""
Core analysis endpoint: resume ↔ job description matching.
"""
import json
from collections import Counter
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisSummary,
    DashboardResponse,
    InterviewPack,
    InterviewQuestion,
    Roadmap,
    RoadmapMilestone,
    ScoreBreakdown,
    SkillOverlap,
)
from app.core.database import get_db
from app.models.analysis import JobDescription, MatchAnalysis, Resume
from app.models.user import User
from app.services.interview_gen import InterviewQuestionGenerator
from app.services.llm_service import LLMService
from app.services.roadmap_generator import RoadmapGenerator
from app.services.scorer import MatchScorer

router = APIRouter(prefix="/analysis", tags=["analysis"])

_scorer = MatchScorer()
_roadmap_gen = RoadmapGenerator()
_interview_gen = InterviewQuestionGenerator()
_llm = LLMService()


@router.post("/", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
def run_analysis(
    payload: AnalysisRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    resume = db.query(Resume).filter(
        Resume.id == payload.resume_id, Resume.user_id == current_user.id
    ).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    jd = db.query(JobDescription).filter(
        JobDescription.id == payload.job_description_id,
        JobDescription.user_id == current_user.id,
    ).first()
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")

    # ── Core scoring ──────────────────────────────────────────────────────────
    resume_skills = resume.get_skills()
    jd_skills = jd.get_required_skills()

    match = _scorer.score(
        resume_text=resume.raw_text,
        jd_text=jd.raw_text,
        resume_skills=resume_skills,
        jd_skills=jd_skills,
    )

    # ── Optional LLM enrichment ───────────────────────────────────────────────
    suggestions = match.suggestions
    llm_suggestions = _llm.enrich_suggestions({
        "role": jd.title,
        "score": match.overall_score,
        "missing_skills": match.missing_skills,
        "keyword_gaps": match.keyword_gaps,
    })
    if llm_suggestions:
        suggestions = llm_suggestions

    # ── Roadmap ───────────────────────────────────────────────────────────────
    roadmap_data = _roadmap_gen.generate(match.missing_skills, role_title=jd.title)

    # ── Interview questions ───────────────────────────────────────────────────
    interview_data = _interview_gen.generate(
        matching_skills=match.matching_skills,
        missing_skills=match.missing_skills,
        role_title=jd.title,
    )

    # ── Persist ───────────────────────────────────────────────────────────────
    analysis = MatchAnalysis(
        user_id=current_user.id,
        resume_id=resume.id,
        job_description_id=jd.id,
        overall_score=match.overall_score,
        semantic_score=match.semantic_score,
        keyword_score=match.keyword_score,
        skill_overlap_score=match.skill_overlap_score,
        confidence=match.confidence,
        matching_skills=json.dumps(match.matching_skills),
        missing_skills=json.dumps(match.missing_skills),
        keyword_gaps=json.dumps(match.keyword_gaps),
        suggestions=json.dumps(suggestions),
        learning_roadmap=json.dumps(roadmap_data),
        interview_questions=json.dumps(interview_data),
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return _build_response(analysis, match, roadmap_data, interview_data, suggestions)


@router.get("/", response_model=list[AnalysisSummary])
def list_analyses(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    analyses = (
        db.query(MatchAnalysis, JobDescription)
        .join(JobDescription, MatchAnalysis.job_description_id == JobDescription.id)
        .filter(MatchAnalysis.user_id == current_user.id)
        .order_by(MatchAnalysis.created_at.desc())
        .all()
    )
    return [
        AnalysisSummary(
            id=a.id,
            job_title=jd.title,
            company=jd.company,
            overall_score=round(a.overall_score * 100, 1),
            grade=_grade(a.overall_score),
            created_at=a.created_at,
        )
        for a, jd in analyses
    ]


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    analyses = (
        db.query(MatchAnalysis, JobDescription)
        .join(JobDescription, MatchAnalysis.job_description_id == JobDescription.id)
        .filter(MatchAnalysis.user_id == current_user.id)
        .order_by(MatchAnalysis.created_at.desc())
        .all()
    )

    if not analyses:
        return DashboardResponse(
            total_analyses=0,
            average_score=0.0,
            best_match=None,
            recent_analyses=[],
            top_missing_skills=[],
            top_matching_skills=[],
        )

    summaries = [
        AnalysisSummary(
            id=a.id,
            job_title=jd.title,
            company=jd.company,
            overall_score=round(a.overall_score * 100, 1),
            grade=_grade(a.overall_score),
            created_at=a.created_at,
        )
        for a, jd in analyses
    ]

    all_missing: list[str] = []
    all_matching: list[str] = []
    for a, _ in analyses:
        all_missing.extend(json.loads(a.missing_skills or "[]"))
        all_matching.extend(json.loads(a.matching_skills or "[]"))

    avg_score = sum(a.overall_score for a, _ in analyses) / len(analyses)
    best = max(analyses, key=lambda x: x[0].overall_score)

    return DashboardResponse(
        total_analyses=len(analyses),
        average_score=round(avg_score * 100, 1),
        best_match=AnalysisSummary(
            id=best[0].id,
            job_title=best[1].title,
            company=best[1].company,
            overall_score=round(best[0].overall_score * 100, 1),
            grade=_grade(best[0].overall_score),
            created_at=best[0].created_at,
        ),
        recent_analyses=summaries[:10],
        top_missing_skills=[s for s, _ in Counter(all_missing).most_common(10)],
        top_matching_skills=[s for s, _ in Counter(all_matching).most_common(10)],
    )


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(
    analysis_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    analysis = db.query(MatchAnalysis).filter(
        MatchAnalysis.id == analysis_id, MatchAnalysis.user_id == current_user.id
    ).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    roadmap_data = json.loads(analysis.learning_roadmap or "{}")
    interview_data = json.loads(analysis.interview_questions or "{}")
    suggestions = json.loads(analysis.suggestions or "[]")

    from app.services.scorer import MatchScore
    match = MatchScore(
        overall_score=analysis.overall_score,
        semantic_score=analysis.semantic_score,
        keyword_score=analysis.keyword_score,
        skill_overlap_score=analysis.skill_overlap_score,
        confidence=analysis.confidence,
        matching_skills=json.loads(analysis.matching_skills or "[]"),
        missing_skills=json.loads(analysis.missing_skills or "[]"),
        keyword_gaps=json.loads(analysis.keyword_gaps or "[]"),
        suggestions=suggestions,
    )

    return _build_response(analysis, match, roadmap_data, interview_data, suggestions)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _grade(score: float) -> str:
    if score >= 0.85:
        return "Excellent"
    elif score >= 0.70:
        return "Strong"
    elif score >= 0.55:
        return "Good"
    elif score >= 0.40:
        return "Fair"
    return "Needs Work"


def _build_response(analysis, match, roadmap_data, interview_data, suggestions) -> AnalysisResponse:
    from app.services.scorer import MatchScore as MS

    roadmap_milestones = [
        RoadmapMilestone(
            skill=m["skill"],
            level=m["level"],
            estimated_weeks=m["estimated_weeks"],
            resources=m["resources"],
        )
        for m in roadmap_data.get("milestones", [])
    ]

    roadmap = Roadmap(
        role_target=roadmap_data.get("role_target", ""),
        estimated_total_weeks=roadmap_data.get("estimated_total_weeks", 0),
        phases=roadmap_data.get("phases", []),
        milestones=roadmap_milestones,
        quick_wins=roadmap_data.get("quick_wins", []),
    )

    tech_qs = [
        InterviewQuestion(**q) if isinstance(q, dict) else q
        for q in interview_data.get("technical_questions", [])
    ]
    interview_pack = InterviewPack(
        role=interview_data.get("role", ""),
        technical_questions=tech_qs,
        behavioral_questions=interview_data.get("behavioral_questions", []),
        system_design_questions=interview_data.get("system_design_questions", []),
        total_count=interview_data.get("total_count", 0),
    )

    score = match if isinstance(match, dict) else match
    overall = score.overall_score if hasattr(score, "overall_score") else score["overall_score"]
    semantic = score.semantic_score if hasattr(score, "semantic_score") else score["semantic_score"]
    kw = score.keyword_score if hasattr(score, "keyword_score") else score["keyword_score"]
    sk = score.skill_overlap_score if hasattr(score, "skill_overlap_score") else score["skill_overlap_score"]
    conf = score.confidence if hasattr(score, "confidence") else score["confidence"]
    matching = score.matching_skills if hasattr(score, "matching_skills") else score.get("matching_skills", [])
    missing = score.missing_skills if hasattr(score, "missing_skills") else score.get("missing_skills", [])
    extra = score.extra_skills if hasattr(score, "extra_skills") else []
    kw_gaps = score.keyword_gaps if hasattr(score, "keyword_gaps") else score.get("keyword_gaps", [])
    kw_hits = score.keyword_hits if hasattr(score, "keyword_hits") else []

    return AnalysisResponse(
        id=analysis.id,
        resume_id=analysis.resume_id,
        job_description_id=analysis.job_description_id,
        score=ScoreBreakdown(
            overall_score=round(overall * 100, 1),
            semantic_score=round(semantic * 100, 1),
            keyword_score=round(kw * 100, 1),
            skill_overlap_score=round(sk * 100, 1),
            confidence=round(conf * 100, 1),
            grade=_grade(overall),
        ),
        skill_overlap=SkillOverlap(
            matching_skills=matching,
            missing_skills=missing,
            extra_skills=extra,
        ),
        keyword_gaps=kw_gaps,
        keyword_hits=kw_hits,
        suggestions=suggestions,
        roadmap=roadmap,
        interview_pack=interview_pack,
        created_at=analysis.created_at,
    )
