"""
Export endpoint: generates markdown or PDF reports from analysis results.
"""
import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse, Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.analysis import JobDescription, MatchAnalysis, Resume
from app.models.user import User

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/{analysis_id}/markdown", response_class=PlainTextResponse)
def export_markdown(
    analysis_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    analysis, resume, jd = _get_analysis_with_relations(analysis_id, current_user.id, db)
    md = _render_markdown(analysis, resume, jd)
    return PlainTextResponse(content=md, media_type="text/markdown")


@router.get("/{analysis_id}/pdf")
def export_pdf(
    analysis_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    analysis, resume, jd = _get_analysis_with_relations(analysis_id, current_user.id, db)
    md = _render_markdown(analysis, resume, jd)

    try:
        import markdown2
        import weasyprint

        html = markdown2.markdown(md, extras=["tables", "fenced-code-blocks"])
        styled_html = f"""
        <!DOCTYPE html><html><head>
        <meta charset="UTF-8">
        <style>
          body {{ font-family: 'Helvetica', sans-serif; margin: 40px; color: #1a202c; line-height: 1.6; }}
          h1 {{ color: #2563eb; }} h2 {{ color: #374151; border-bottom: 1px solid #e5e7eb; padding-bottom: 4px; }}
          h3 {{ color: #4b5563; }} table {{ border-collapse: collapse; width: 100%; }}
          td, th {{ border: 1px solid #e5e7eb; padding: 8px; }} th {{ background: #f3f4f6; }}
          code {{ background: #f3f4f6; padding: 2px 4px; border-radius: 3px; }}
        </style></head><body>{html}</body></html>"""
        pdf_bytes = weasyprint.HTML(string=styled_html).write_pdf()
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=recruitiq_analysis_{analysis_id}.pdf"},
        )
    except ImportError:
        # Fallback: return markdown as plain text
        return PlainTextResponse(
            content=md,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename=recruitiq_analysis_{analysis_id}.md"},
        )


def _get_analysis_with_relations(analysis_id, user_id, db: Session):
    analysis = db.query(MatchAnalysis).filter(
        MatchAnalysis.id == analysis_id, MatchAnalysis.user_id == user_id
    ).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    resume = db.query(Resume).filter(Resume.id == analysis.resume_id).first()
    jd = db.query(JobDescription).filter(JobDescription.id == analysis.job_description_id).first()
    return analysis, resume, jd


def _render_markdown(analysis: MatchAnalysis, resume: Resume, jd: JobDescription) -> str:
    matching = json.loads(analysis.matching_skills or "[]")
    missing = json.loads(analysis.missing_skills or "[]")
    kw_gaps = json.loads(analysis.keyword_gaps or "[]")
    suggestions = json.loads(analysis.suggestions or "[]")
    roadmap = json.loads(analysis.learning_roadmap or "{}")
    interview = json.loads(analysis.interview_questions or "{}")

    def grade(s):
        if s >= 0.85: return "Excellent"
        elif s >= 0.70: return "Strong"
        elif s >= 0.55: return "Good"
        elif s >= 0.40: return "Fair"
        return "Needs Work"

    lines = [
        f"# RecruitIQ — Match Analysis Report",
        f"",
        f"**Resume:** {resume.filename}  ",
        f"**Job Title:** {jd.title}  ",
        f"**Company:** {jd.company or 'N/A'}  ",
        f"",
        f"---",
        f"",
        f"## Score Overview",
        f"",
        f"| Metric | Score |",
        f"|--------|-------|",
        f"| **Overall Match** | **{analysis.overall_score * 100:.1f}% — {grade(analysis.overall_score)}** |",
        f"| Semantic Similarity | {analysis.semantic_score * 100:.1f}% |",
        f"| Keyword Coverage | {analysis.keyword_score * 100:.1f}% |",
        f"| Skill Overlap | {analysis.skill_overlap_score * 100:.1f}% |",
        f"| Confidence | {analysis.confidence * 100:.1f}% |",
        f"",
        f"---",
        f"",
        f"## Skill Analysis",
        f"",
        f"### Matching Skills ({len(matching)})",
        ", ".join(f"`{s}`" for s in matching) or "_None found_",
        f"",
        f"### Missing Skills ({len(missing)})",
        ", ".join(f"`{s}`" for s in missing) or "_None identified_",
        f"",
        f"### Top Keyword Gaps",
        ", ".join(f"`{k}`" for k in kw_gaps[:15]) or "_None_",
        f"",
        f"---",
        f"",
        f"## Improvement Suggestions",
        f"",
    ]
    for i, s in enumerate(suggestions, 1):
        lines.append(f"{i}. {s}")

    lines += [
        f"",
        f"---",
        f"",
        f"## Learning Roadmap",
        f"",
        f"**Target Role:** {roadmap.get('role_target', jd.title)}  ",
        f"**Estimated Time:** {roadmap.get('estimated_total_weeks', 0)} weeks  ",
        f"",
    ]
    for phase in roadmap.get("phases", []):
        lines.append(f"### Phase: {phase['phase']}")
        for skill in phase["skills"]:
            lines.append(f"- {skill}")
        lines.append("")

    if roadmap.get("quick_wins"):
        lines += [
            f"### Quick Wins (≤2 weeks)",
            ", ".join(roadmap["quick_wins"]),
            "",
        ]

    lines += [
        f"---",
        f"",
        f"## Interview Preparation",
        f"",
        f"### Technical Questions",
        f"",
    ]
    for q in interview.get("technical_questions", []):
        lines.append(f"**[{q.get('skill', '')} — {q.get('type', '')}]** {q.get('question', '')}  ")
        lines.append(f"> _{q.get('note', '')}_")
        lines.append("")

    lines += [f"### Behavioral Questions", ""]
    for q in interview.get("behavioral_questions", []):
        lines.append(f"- {q}")

    lines += [f"", f"### System Design Questions", ""]
    for q in interview.get("system_design_questions", []):
        lines.append(f"- {q}")

    lines += ["", "---", "_Generated by RecruitIQ — AI-Powered Career Intelligence_"]
    return "\n".join(lines)
