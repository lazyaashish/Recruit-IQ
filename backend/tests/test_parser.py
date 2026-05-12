"""Tests for document parsing and skill extraction."""
import pytest

from app.services.parser import JobDescriptionParser, ResumeParser
from app.services.skill_extractor import SkillExtractor

SAMPLE_RESUME = """
Jane Doe
jane@example.com | github.com/janedoe | linkedin.com/in/janedoe

SUMMARY
ML Engineer with 4 years of experience building production NLP systems.

SKILLS
Python, PyTorch, scikit-learn, NLP, Hugging Face Transformers, FastAPI, Docker

EXPERIENCE
Senior ML Engineer – Acme AI (2022–Present)
- Built a sentence-transformer-based semantic search engine (FAISS, 10M docs)
- Fine-tuned LLMs using LoRA for domain adaptation
- Deployed models via FastAPI + Docker, achieving p95 latency < 80ms

EDUCATION
BSc Computer Science – University of Example, 2020
"""

SAMPLE_JD = """
AI/ML Engineer – TechCorp

Requirements:
- 3+ years Python experience
- Deep knowledge of PyTorch or TensorFlow
- Experience with Hugging Face Transformers and LLM fine-tuning
- Familiarity with RAG and vector databases (FAISS, Chroma)
- FastAPI or Flask for API development
- Docker and CI/CD pipelines
- Strong understanding of NLP fundamentals

Nice to have:
- MLflow experiment tracking
- AWS SageMaker or GCP Vertex AI
"""


def test_resume_parser_extracts_sections():
    parser = ResumeParser()
    result = parser.parse(SAMPLE_RESUME)
    assert "skills" in result.sections
    assert "experience" in result.sections


def test_resume_parser_extracts_contact():
    parser = ResumeParser()
    result = parser.parse(SAMPLE_RESUME)
    assert result.contact_info.get("email") == "jane@example.com"
    assert "janedoe" in result.contact_info.get("github", "")


def test_jd_parser_extracts_title():
    parser = JobDescriptionParser()
    result = parser.parse(SAMPLE_JD)
    assert "AI" in result.title or "Engineer" in result.title


def test_skill_extractor_finds_skills():
    extractor = SkillExtractor()
    skills = extractor.extract(SAMPLE_RESUME)
    assert "Python" in skills
    assert "PyTorch" in skills
    assert "FastAPI" in skills


def test_skill_extractor_finds_jd_skills():
    extractor = SkillExtractor()
    skills = extractor.extract(SAMPLE_JD)
    assert "PyTorch" in skills
    assert "Docker" in skills
    assert "NLP" in skills


def test_skill_overlap():
    extractor = SkillExtractor()
    resume_skills = extractor.extract(SAMPLE_RESUME)
    jd_skills = extractor.extract(SAMPLE_JD)
    overlap = extractor.compute_overlap(resume_skills, jd_skills)
    assert overlap["overlap_score"] >= 0.0
    assert len(overlap["matching_skills"]) >= 1
    assert isinstance(overlap["missing_skills"], list)


def test_skill_extractor_confidence_scores():
    extractor = SkillExtractor()
    results = extractor.extract_with_scores(SAMPLE_RESUME)
    assert len(results) > 0
    for r in results:
        assert 0.0 <= r["confidence"] <= 1.0
        assert r["mentions"] >= 1
