"""
Learning roadmap generation service.
Uses deterministic skill-to-resource mapping + optional LLM enrichment.
"""
from __future__ import annotations

from app.core.logging import get_logger

logger = get_logger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Curated learning resource map per skill
# ─────────────────────────────────────────────────────────────────────────────
SKILL_RESOURCES: dict[str, dict] = {
    "Python": {
        "level": "Foundational",
        "resources": [
            {"type": "course", "title": "Python for Everybody – Coursera (UMich)", "url": "https://www.coursera.org/specializations/python"},
            {"type": "book", "title": "Fluent Python, 2nd Ed. – Luciano Ramalho"},
        ],
        "estimated_weeks": 4,
    },
    "Machine Learning": {
        "level": "Foundational",
        "resources": [
            {"type": "course", "title": "Machine Learning Specialization – Andrew Ng (Coursera)", "url": "https://www.coursera.org/specializations/machine-learning-introduction"},
            {"type": "book", "title": "Hands-On ML with Scikit-Learn, Keras & TensorFlow – Aurélien Géron"},
        ],
        "estimated_weeks": 8,
    },
    "Deep Learning": {
        "level": "Intermediate",
        "resources": [
            {"type": "course", "title": "Deep Learning Specialization – deeplearning.ai", "url": "https://www.coursera.org/specializations/deep-learning"},
            {"type": "course", "title": "fast.ai Practical Deep Learning", "url": "https://course.fast.ai"},
        ],
        "estimated_weeks": 10,
    },
    "PyTorch": {
        "level": "Intermediate",
        "resources": [
            {"type": "docs", "title": "PyTorch Official Tutorials", "url": "https://pytorch.org/tutorials"},
            {"type": "course", "title": "PyTorch for Deep Learning – Zero to Mastery", "url": "https://www.zerotomastery.io/courses/pytorch"},
        ],
        "estimated_weeks": 5,
    },
    "NLP": {
        "level": "Intermediate",
        "resources": [
            {"type": "course", "title": "Hugging Face NLP Course (free)", "url": "https://huggingface.co/learn/nlp-course"},
            {"type": "book", "title": "Natural Language Processing with Transformers – Lewis Tunstall"},
        ],
        "estimated_weeks": 6,
    },
    "LLM Engineering": {
        "level": "Advanced",
        "resources": [
            {"type": "course", "title": "LLM Bootcamp – The Full Stack", "url": "https://fullstackdeeplearning.com/llm-bootcamp"},
            {"type": "docs", "title": "OpenAI Cookbook", "url": "https://github.com/openai/openai-cookbook"},
        ],
        "estimated_weeks": 6,
    },
    "RAG": {
        "level": "Advanced",
        "resources": [
            {"type": "tutorial", "title": "LangChain RAG Guide", "url": "https://python.langchain.com/docs/use_cases/question_answering"},
            {"type": "paper", "title": "RAG Paper – Lewis et al. (2020)", "url": "https://arxiv.org/abs/2005.11401"},
        ],
        "estimated_weeks": 3,
    },
    "Embeddings": {
        "level": "Intermediate",
        "resources": [
            {"type": "docs", "title": "Sentence Transformers Documentation", "url": "https://www.sbert.net"},
            {"type": "tutorial", "title": "Word2Vec + GloVe from Scratch – Jay Alammar", "url": "https://jalammar.github.io/illustrated-word2vec"},
        ],
        "estimated_weeks": 2,
    },
    "MLflow": {
        "level": "Intermediate",
        "resources": [
            {"type": "docs", "title": "MLflow Quickstart Guide", "url": "https://mlflow.org/docs/latest/quickstart.html"},
        ],
        "estimated_weeks": 1,
    },
    "Docker": {
        "level": "Foundational",
        "resources": [
            {"type": "course", "title": "Docker & Kubernetes – Udemy (Bret Fisher)", "url": "https://www.udemy.com/course/docker-mastery"},
        ],
        "estimated_weeks": 2,
    },
    "FastAPI": {
        "level": "Foundational",
        "resources": [
            {"type": "docs", "title": "FastAPI Official Tutorial", "url": "https://fastapi.tiangolo.com/tutorial"},
        ],
        "estimated_weeks": 1,
    },
    "FAISS": {
        "level": "Intermediate",
        "resources": [
            {"type": "docs", "title": "FAISS Wiki – Facebook Research", "url": "https://github.com/facebookresearch/faiss/wiki"},
        ],
        "estimated_weeks": 1,
    },
    "Hugging Face": {
        "level": "Intermediate",
        "resources": [
            {"type": "course", "title": "Hugging Face Transformers Course (free)", "url": "https://huggingface.co/learn/nlp-course"},
            {"type": "docs", "title": "Transformers Library Docs", "url": "https://huggingface.co/docs/transformers"},
        ],
        "estimated_weeks": 4,
    },
    "Fine-tuning": {
        "level": "Advanced",
        "resources": [
            {"type": "tutorial", "title": "LoRA + QLoRA Fine-Tuning Guide – Sebastian Raschka", "url": "https://lightning.ai/pages/community/lora-insights"},
            {"type": "docs", "title": "PEFT Library – Hugging Face", "url": "https://huggingface.co/docs/peft"},
        ],
        "estimated_weeks": 4,
    },
    "AWS": {
        "level": "Intermediate",
        "resources": [
            {"type": "course", "title": "AWS Machine Learning Specialty Prep – A Cloud Guru"},
            {"type": "docs", "title": "AWS SageMaker Developer Guide", "url": "https://docs.aws.amazon.com/sagemaker"},
        ],
        "estimated_weeks": 4,
    },
    "scikit-learn": {
        "level": "Foundational",
        "resources": [
            {"type": "docs", "title": "scikit-learn User Guide", "url": "https://scikit-learn.org/stable/user_guide.html"},
        ],
        "estimated_weeks": 3,
    },
    "Prompt Engineering": {
        "level": "Intermediate",
        "resources": [
            {"type": "guide", "title": "Prompt Engineering Guide – DAIR.AI", "url": "https://www.promptingguide.ai"},
        ],
        "estimated_weeks": 1,
    },
    "Model Evaluation": {
        "level": "Intermediate",
        "resources": [
            {"type": "book", "title": "Evaluating Machine Learning Models – Alice Zheng (O'Reilly)"},
        ],
        "estimated_weeks": 2,
    },
}

LEVEL_ORDER = {"Foundational": 0, "Intermediate": 1, "Advanced": 2}


class RoadmapGenerator:
    """
    Generates a personalized, time-estimated learning roadmap
    based on the candidate's skill gaps.
    """

    def generate(self, missing_skills: list[str], role_title: str = "AI/ML Engineer") -> dict:
        """
        Returns a structured roadmap with phases, resources, and total weeks.
        """
        milestones = self._build_milestones(missing_skills)
        total_weeks = sum(m["estimated_weeks"] for m in milestones)

        return {
            "role_target": role_title,
            "total_skills_to_learn": len(missing_skills),
            "estimated_total_weeks": total_weeks,
            "milestones": milestones,
            "phases": self._group_into_phases(milestones),
            "quick_wins": self._identify_quick_wins(milestones),
        }

    def _build_milestones(self, missing_skills: list[str]) -> list[dict]:
        milestones = []
        for skill in missing_skills:
            resource_info = SKILL_RESOURCES.get(skill)
            if resource_info:
                milestones.append({
                    "skill": skill,
                    "level": resource_info["level"],
                    "resources": resource_info["resources"],
                    "estimated_weeks": resource_info["estimated_weeks"],
                })
            else:
                # Generic fallback for unknown skills
                milestones.append({
                    "skill": skill,
                    "level": "Intermediate",
                    "resources": [
                        {"type": "search", "title": f"Search: '{skill} tutorial site:github.com OR site:medium.com'"}
                    ],
                    "estimated_weeks": 2,
                })

        # Sort: Foundational first, then Intermediate, then Advanced
        milestones.sort(key=lambda m: LEVEL_ORDER.get(m["level"], 1))
        return milestones

    def _group_into_phases(self, milestones: list[dict]) -> list[dict]:
        phases: dict[str, list] = {"Foundational": [], "Intermediate": [], "Advanced": []}
        for m in milestones:
            level = m["level"]
            if level in phases:
                phases[level].append(m["skill"])

        result = []
        for phase_name, skills in phases.items():
            if skills:
                result.append({"phase": phase_name, "skills": skills})
        return result

    def _identify_quick_wins(self, milestones: list[dict]) -> list[str]:
        """Skills learnable in ≤2 weeks."""
        return [m["skill"] for m in milestones if m["estimated_weeks"] <= 2]
