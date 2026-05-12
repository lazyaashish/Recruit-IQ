"""Tests for the match scoring engine."""
import pytest

from app.services.scorer import MatchScorer

RESUME = """
Python developer with 3 years of experience in machine learning.
Proficient in PyTorch, scikit-learn, and NLP. Built transformer-based
text classifiers and deployed FastAPI services using Docker.
"""

JD = """
We are looking for an ML Engineer with Python, PyTorch, NLP experience.
Must know FastAPI and Docker. Experience with Hugging Face transformers a plus.
"""

UNRELATED_JD = """
Senior DevOps Engineer — Kubernetes, Terraform, AWS infrastructure.
Must have 5+ years managing cloud infrastructure and CI/CD pipelines.
No ML experience required.
"""


def test_scorer_returns_valid_score():
    scorer = MatchScorer()
    result = scorer.score(RESUME, JD)
    assert 0.0 <= result.overall_score <= 1.0
    assert 0.0 <= result.semantic_score <= 1.0
    assert 0.0 <= result.confidence <= 1.0


def test_scorer_high_similarity_for_matching_content():
    scorer = MatchScorer()
    result = scorer.score(RESUME, JD)
    # Should score notably above 0 for clearly related content
    assert result.overall_score > 0.1


def test_scorer_detects_matching_skills():
    scorer = MatchScorer()
    result = scorer.score(RESUME, JD)
    assert len(result.matching_skills) > 0


def test_scorer_grade_property():
    scorer = MatchScorer()
    result = scorer.score(RESUME, JD)
    assert result.grade in {"Excellent", "Strong", "Good", "Fair", "Needs Work"}


def test_scorer_produces_suggestions():
    scorer = MatchScorer()
    result = scorer.score(RESUME, JD)
    assert isinstance(result.suggestions, list)


def test_scorer_dict_output():
    scorer = MatchScorer()
    result = scorer.score(RESUME, JD)
    d = result.to_dict()
    assert "overall_score" in d
    assert "matching_skills" in d
    assert "missing_skills" in d
