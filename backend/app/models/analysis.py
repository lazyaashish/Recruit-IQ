"""Analysis, Resume, and JobDescription models."""
import json
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_sections: Mapped[str] = mapped_column(Text, nullable=True)  # JSON
    skills: Mapped[str] = mapped_column(Text, nullable=True)           # JSON list
    embedding_id: Mapped[str] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    def get_skills(self) -> list[str]:
        return json.loads(self.skills) if self.skills else []

    def get_parsed_sections(self) -> dict:
        return json.loads(self.parsed_sections) if self.parsed_sections else {}


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    required_skills: Mapped[str] = mapped_column(Text, nullable=True)  # JSON list
    embedding_id: Mapped[str] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    def get_required_skills(self) -> list[str]:
        return json.loads(self.required_skills) if self.required_skills else []


class MatchAnalysis(Base):
    __tablename__ = "match_analyses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    resume_id: Mapped[int] = mapped_column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_description_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("job_descriptions.id"), nullable=False
    )

    # Scoring
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    semantic_score: Mapped[float] = mapped_column(Float, nullable=False)
    keyword_score: Mapped[float] = mapped_column(Float, nullable=False)
    skill_overlap_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)

    # Analysis results (JSON)
    matching_skills: Mapped[str] = mapped_column(Text, nullable=True)
    missing_skills: Mapped[str] = mapped_column(Text, nullable=True)
    keyword_gaps: Mapped[str] = mapped_column(Text, nullable=True)
    suggestions: Mapped[str] = mapped_column(Text, nullable=True)
    learning_roadmap: Mapped[str] = mapped_column(Text, nullable=True)
    interview_questions: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
