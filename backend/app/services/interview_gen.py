"""
Interview question generation service.
Uses deterministic templates + optional LLM enrichment.
Fully functional without an LLM — LLM layer only enhances output.
"""
from __future__ import annotations

import random
from typing import Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Deterministic question bank keyed by skill
# ─────────────────────────────────────────────────────────────────────────────
QUESTION_BANK: dict[str, list[str]] = {
    "Python": [
        "Explain the difference between a list, tuple, and generator in Python.",
        "How does Python's GIL affect multi-threaded ML training pipelines?",
        "Walk me through how you'd use asyncio to handle concurrent API calls in a data pipeline.",
    ],
    "Machine Learning": [
        "Explain the bias-variance tradeoff and how you manage it in practice.",
        "How would you approach a class-imbalanced classification problem?",
        "What validation strategy would you use for time-series data and why?",
    ],
    "Deep Learning": [
        "Explain vanishing gradients and how techniques like batch norm and residual connections address them.",
        "How does attention differ from convolution for sequence modeling tasks?",
        "Describe the architecture of a transformer. What is multi-head attention doing?",
    ],
    "NLP": [
        "How do you handle out-of-vocabulary tokens in a production NLP system?",
        "Explain the difference between BM25 retrieval and dense vector retrieval.",
        "Walk me through building a text classification pipeline from scratch.",
    ],
    "LLM Engineering": [
        "How would you reduce hallucinations in a production LLM application?",
        "What's the difference between in-context learning, fine-tuning, and RAG? When do you use each?",
        "Describe your approach to evaluating an LLM-based feature end-to-end.",
    ],
    "RAG": [
        "What are the main failure modes of RAG systems and how do you debug them?",
        "How would you choose between sparse and dense retrieval for a Q&A system?",
        "Describe how you'd implement hybrid search combining BM25 and embeddings.",
    ],
    "Embeddings": [
        "How do you pick the right embedding model for a task? What trade-offs matter?",
        "Explain the role of contrastive learning in training better embeddings.",
        "How do you handle embedding drift as documents or queries change over time?",
    ],
    "MLflow": [
        "How do you track experiments across a team to ensure reproducibility?",
        "What metadata would you log for an NLP fine-tuning run to make it fully reproducible?",
    ],
    "PyTorch": [
        "Explain the difference between .detach() and .no_grad() in PyTorch.",
        "How do you debug NaN losses during training?",
        "Walk me through writing a custom Dataset and DataLoader for a multi-modal task.",
    ],
    "scikit-learn": [
        "How do you build a production-grade pipeline in scikit-learn that prevents data leakage?",
        "What's the difference between GridSearchCV and RandomizedSearchCV? When would you use Bayesian optimization instead?",
    ],
    "Docker": [
        "How do you structure a multi-stage Dockerfile for a Python ML service to minimize image size?",
        "What's your strategy for managing GPU access inside containers?",
    ],
    "FastAPI": [
        "How do you add proper dependency injection and request validation in FastAPI?",
        "Describe how you'd implement background tasks and rate limiting in a FastAPI ML service.",
    ],
    "Fine-tuning": [
        "Explain LoRA and why it makes fine-tuning large models practical.",
        "How do you decide the learning rate schedule and batch size when fine-tuning an LLM?",
        "Describe your evaluation process after fine-tuning to check for regression.",
    ],
    "Model Evaluation": [
        "How do you evaluate a ranking model vs. a classification model?",
        "What's your approach to offline vs. online evaluation for an ML feature?",
        "Describe a scenario where accuracy was a misleading metric and what you used instead.",
    ],
    "AWS": [
        "How would you deploy an ML model as a scalable endpoint on AWS?",
        "Explain the role of SageMaker Pipelines in a production ML workflow.",
    ],
    "Prompt Engineering": [
        "What is chain-of-thought prompting and when does it help?",
        "How do you design a few-shot prompt for a novel classification task?",
    ],
}

BEHAVIORAL_QUESTIONS = [
    "Tell me about a time you had to debug a model that was performing well offline but poorly in production.",
    "Describe a project where you had to communicate ML results to non-technical stakeholders.",
    "Walk me through the most complex ML system you've built end-to-end.",
    "How do you prioritize technical debt vs. shipping new model features?",
    "Tell me about a failed experiment and what you learned from it.",
    "Describe a time you had to work with messy, incomplete data. How did you handle it?",
]

SYSTEM_DESIGN_QUESTIONS = [
    "Design a real-time recommendation system for a news feed. Walk me through the ML architecture.",
    "How would you build a semantic search engine for a large document corpus?",
    "Design an A/B testing framework for continuous ML model evaluation.",
    "How would you architect a multi-tenant AI platform where each customer has custom models?",
    "Design a pipeline to monitor model drift and trigger automatic retraining.",
]


class InterviewQuestionGenerator:
    """
    Generates tailored interview questions based on:
    - Matching skills (expect depth questions)
    - Missing skills (gap awareness questions)
    - Role type
    Optionally enriches with LLM-generated personalized questions.
    """

    def generate(
        self,
        matching_skills: list[str],
        missing_skills: list[str],
        role_title: str = "AI/ML Engineer",
        use_llm: bool = False,
        llm_service=None,
    ) -> dict:
        technical_questions = self._get_technical_questions(matching_skills, missing_skills)
        behavioral = random.sample(BEHAVIORAL_QUESTIONS, min(3, len(BEHAVIORAL_QUESTIONS)))
        system_design = random.sample(SYSTEM_DESIGN_QUESTIONS, min(2, len(SYSTEM_DESIGN_QUESTIONS)))

        return {
            "role": role_title,
            "technical_questions": technical_questions,
            "behavioral_questions": behavioral,
            "system_design_questions": system_design,
            "total_count": (
                len(technical_questions) + len(behavioral) + len(system_design)
            ),
        }

    def _get_technical_questions(
        self, matching_skills: list[str], missing_skills: list[str]
    ) -> list[dict]:
        questions = []

        # Depth questions for matching skills (you'll be tested on these)
        for skill in matching_skills[:6]:
            skill_qs = QUESTION_BANK.get(skill, [])
            if skill_qs:
                q = random.choice(skill_qs)
                questions.append({
                    "question": q,
                    "skill": skill,
                    "type": "depth",
                    "note": "Expected to answer confidently — this is on your resume.",
                })

        # Gap awareness questions for missing skills
        for skill in missing_skills[:4]:
            skill_qs = QUESTION_BANK.get(skill, [])
            if skill_qs:
                q = random.choice(skill_qs)
                questions.append({
                    "question": q,
                    "skill": skill,
                    "type": "gap_awareness",
                    "note": "This skill is in the JD but not your resume — prepare an honest answer.",
                })

        return questions
