"""
Match scoring engine.
Combines semantic similarity, keyword overlap, and skill overlap
into a weighted, explainable composite score.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from app.core.logging import get_logger
from app.services.embedder import EmbeddingService
from app.services.skill_extractor import SkillExtractor

logger = get_logger(__name__)

# Scoring weights — transparent and tunable
WEIGHTS = {
    "semantic": 0.45,      # Semantic similarity (embeddings)
    "skill_overlap": 0.35,  # Skill set overlap
    "keyword": 0.20,        # Keyword/TF coverage
}


@dataclass
class MatchScore:
    overall_score: float
    semantic_score: float
    keyword_score: float
    skill_overlap_score: float
    confidence: float

    matching_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    extra_skills: list[str] = field(default_factory=list)
    keyword_gaps: list[str] = field(default_factory=list)
    keyword_hits: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "overall_score": round(self.overall_score * 100, 1),
            "semantic_score": round(self.semantic_score * 100, 1),
            "keyword_score": round(self.keyword_score * 100, 1),
            "skill_overlap_score": round(self.skill_overlap_score * 100, 1),
            "confidence": round(self.confidence * 100, 1),
            "matching_skills": self.matching_skills,
            "missing_skills": self.missing_skills,
            "extra_skills": self.extra_skills,
            "keyword_gaps": self.keyword_gaps,
            "keyword_hits": self.keyword_hits,
            "suggestions": self.suggestions,
        }

    @property
    def grade(self) -> str:
        score = self.overall_score
        if score >= 0.85:
            return "Excellent"
        elif score >= 0.70:
            return "Strong"
        elif score >= 0.55:
            return "Good"
        elif score >= 0.40:
            return "Fair"
        else:
            return "Needs Work"


class MatchScorer:
    """
    Deterministic, explainable scoring of resume vs job description.
    Each sub-score is independently computed and interpretable.
    """

    def __init__(self):
        self._embedder = EmbeddingService()
        self._skill_extractor = SkillExtractor()

    def score(
        self,
        resume_text: str,
        jd_text: str,
        resume_skills: Optional[list[str]] = None,
        jd_skills: Optional[list[str]] = None,
    ) -> MatchScore:
        """Compute full match analysis between resume and JD."""

        # 1. Semantic similarity
        semantic_score = self._embedder.semantic_similarity(resume_text, jd_text)

        # 2. Skill overlap
        if resume_skills is None:
            resume_skills = self._skill_extractor.extract(resume_text)
        if jd_skills is None:
            jd_skills = self._skill_extractor.extract(jd_text)

        overlap = self._skill_extractor.compute_overlap(resume_skills, jd_skills)
        skill_overlap_score = overlap["overlap_score"]

        # 3. Keyword coverage (important JD terms found in resume)
        keywords = self._extract_important_keywords(jd_text)
        keyword_score, keyword_hits, keyword_gaps = self._compute_keyword_score(
            resume_text, keywords
        )

        # 4. Composite weighted score
        overall_score = (
            WEIGHTS["semantic"] * semantic_score
            + WEIGHTS["skill_overlap"] * skill_overlap_score
            + WEIGHTS["keyword"] * keyword_score
        )

        # 5. Confidence: based on signal strength
        confidence = self._compute_confidence(
            resume_text, jd_text, resume_skills, jd_skills
        )

        # 6. Actionable suggestions
        suggestions = self._generate_suggestions(
            overall_score,
            overlap["missing_skills"],
            keyword_gaps,
            resume_text,
            jd_text,
        )

        return MatchScore(
            overall_score=round(overall_score, 4),
            semantic_score=round(semantic_score, 4),
            keyword_score=round(keyword_score, 4),
            skill_overlap_score=round(skill_overlap_score, 4),
            confidence=round(confidence, 4),
            matching_skills=overlap["matching_skills"],
            missing_skills=overlap["missing_skills"],
            extra_skills=overlap["extra_skills"],
            keyword_gaps=keyword_gaps[:20],
            keyword_hits=keyword_hits[:20],
            suggestions=suggestions,
        )

    def _extract_important_keywords(self, jd_text: str) -> list[str]:
        """Extract important single and bi-gram keywords from JD using TF scoring."""
        from sklearn.feature_extraction.text import TfidfVectorizer

        try:
            tfidf = TfidfVectorizer(
                ngram_range=(1, 2),
                stop_words="english",
                max_features=80,
            )
            tfidf.fit([jd_text])
            return list(tfidf.get_feature_names_out())
        except Exception:
            # Fallback: simple word tokenization
            words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#.-]{2,}\b", jd_text)
            stopwords = {"and", "the", "for", "are", "with", "you", "our", "will", "have"}
            return list({w.lower() for w in words if w.lower() not in stopwords})[:80]

    def _compute_keyword_score(
        self, resume_text: str, keywords: list[str]
    ) -> tuple[float, list[str], list[str]]:
        """Check which JD keywords appear in the resume."""
        resume_lower = resume_text.lower()
        hits = [kw for kw in keywords if kw.lower() in resume_lower]
        gaps = [kw for kw in keywords if kw.lower() not in resume_lower]
        score = len(hits) / len(keywords) if keywords else 0.0
        return score, hits, gaps

    def _compute_confidence(
        self,
        resume_text: str,
        jd_text: str,
        resume_skills: list[str],
        jd_skills: list[str],
    ) -> float:
        """
        Confidence is based on:
        - Length of both texts (too short = lower confidence)
        - Number of skills extracted
        """
        resume_words = len(resume_text.split())
        jd_words = len(jd_text.split())

        len_conf = min(1.0, resume_words / 300) * 0.5 + min(1.0, jd_words / 150) * 0.5
        skill_conf = min(1.0, (len(resume_skills) + len(jd_skills)) / 20)

        return round((len_conf + skill_conf) / 2, 4)

    def _generate_suggestions(
        self,
        score: float,
        missing_skills: list[str],
        keyword_gaps: list[str],
        resume_text: str,
        jd_text: str,
    ) -> list[str]:
        """Rule-based actionable suggestions."""
        suggestions = []

        if missing_skills:
            top_missing = missing_skills[:5]
            suggestions.append(
                f"Add these high-priority skills to your resume: {', '.join(top_missing)}"
            )

        if keyword_gaps:
            top_gaps = keyword_gaps[:5]
            suggestions.append(
                f"Incorporate these keywords from the job description: {', '.join(top_gaps)}"
            )

        if score < 0.50:
            suggestions.append(
                "Consider rewriting your summary to align more closely with this role's requirements."
            )

        if "quantif" not in resume_text.lower() and len(re.findall(r"\d+%|\d+x|\$\d+", resume_text)) < 3:
            suggestions.append(
                "Add quantified achievements (e.g., 'improved accuracy by 15%', 'reduced latency by 3x')."
            )

        if "project" not in resume_text.lower():
            suggestions.append(
                "Include relevant AI/ML projects with GitHub links to strengthen your portfolio signal."
            )

        return suggestions
