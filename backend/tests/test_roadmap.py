"""Tests for roadmap and interview question generation."""
from app.services.roadmap_generator import RoadmapGenerator
from app.services.interview_gen import InterviewQuestionGenerator


def test_roadmap_generator_basic():
    gen = RoadmapGenerator()
    result = gen.generate(["PyTorch", "MLflow", "RAG"], role_title="ML Engineer")
    assert result["estimated_total_weeks"] > 0
    assert len(result["milestones"]) == 3
    assert result["role_target"] == "ML Engineer"


def test_roadmap_phases_ordering():
    gen = RoadmapGenerator()
    result = gen.generate(["Python", "LLM Engineering", "scikit-learn"])
    phases = [p["phase"] for p in result["phases"]]
    # Foundational should come before Advanced
    if "Foundational" in phases and "Advanced" in phases:
        assert phases.index("Foundational") < phases.index("Advanced")


def test_roadmap_unknown_skill_fallback():
    gen = RoadmapGenerator()
    result = gen.generate(["SomeObscureTool2025"])
    assert len(result["milestones"]) == 1
    assert result["milestones"][0]["estimated_weeks"] > 0


def test_roadmap_quick_wins():
    gen = RoadmapGenerator()
    result = gen.generate(["FastAPI", "FAISS", "Prompt Engineering"])
    assert isinstance(result["quick_wins"], list)


def test_interview_gen_technical_questions():
    gen = InterviewQuestionGenerator()
    result = gen.generate(
        matching_skills=["Python", "PyTorch", "NLP"],
        missing_skills=["RAG", "MLflow"],
        role_title="ML Engineer"
    )
    assert result["total_count"] > 0
    assert len(result["behavioral_questions"]) > 0
    assert len(result["system_design_questions"]) > 0


def test_interview_gen_question_types():
    gen = InterviewQuestionGenerator()
    result = gen.generate(
        matching_skills=["Python"],
        missing_skills=["Fine-tuning"],
        role_title="LLM Engineer"
    )
    types = {q["type"] for q in result["technical_questions"]}
    # Should have both depth and gap_awareness questions
    assert len(types) >= 1
