"""
Skill extraction service using a curated AI/ML skill taxonomy + NLP matching.
Combines exact match, fuzzy match, and alias resolution.
"""
import re
from typing import Optional

from app.core.logging import get_logger

logger = get_logger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Curated AI/ML/NLP/Engineering skill taxonomy
# ─────────────────────────────────────────────────────────────────────────────
SKILL_TAXONOMY: dict[str, list[str]] = {
    # Languages
    "Python": ["python", "py"],
    "SQL": ["sql", "mysql", "postgresql", "postgres", "sqlite", "t-sql"],
    "R": [r"\bR\b", "rstats"],
    "Scala": ["scala"],
    "Julia": ["julia"],
    "C++": ["c\\+\\+", "cpp"],
    "Java": ["java"],
    "JavaScript": ["javascript", "js", "node.js", "nodejs"],
    "TypeScript": ["typescript", "ts"],
    "Bash": ["bash", "shell scripting", "zsh"],
    "Go": [r"\bgo\b", "golang"],
    # ML / DL Frameworks
    "PyTorch": ["pytorch", "torch"],
    "TensorFlow": ["tensorflow", "tf"],
    "Keras": ["keras"],
    "JAX": ["jax", "flax"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "XGBoost": ["xgboost"],
    "LightGBM": ["lightgbm"],
    "CatBoost": ["catboost"],
    "Hugging Face": ["hugging face", "huggingface", "transformers", "datasets library"],
    # LLMs & Generative AI
    "LLM Engineering": ["llm", "large language model", "language model"],
    "OpenAI API": ["openai", "gpt-3", "gpt-4", "gpt4", "chatgpt api"],
    "Anthropic Claude": ["claude", "anthropic"],
    "LangChain": ["langchain"],
    "LlamaIndex": ["llamaindex", "llama_index", "llama index"],
    "RAG": ["rag", "retrieval-augmented generation", "retrieval augmented"],
    "Prompt Engineering": ["prompt engineering", "prompting"],
    "Fine-tuning": ["fine-tuning", "finetuning", "fine tuning", "rlhf", "lora", "qlora"],
    # NLP
    "NLP": ["nlp", "natural language processing", "text processing"],
    "spaCy": ["spacy"],
    "NLTK": ["nltk"],
    "Text Classification": ["text classification", "sentiment analysis", "topic modeling"],
    "Named Entity Recognition": ["ner", "named entity recognition", "entity extraction"],
    "Embeddings": ["embeddings", "word embeddings", "sentence embeddings", "word2vec", "glove", "fasttext"],
    "Sentence Transformers": ["sentence-transformers", "sentence transformers", "sbert"],
    # MLOps & Infra
    "Docker": ["docker", "dockerfile", "containerization"],
    "Kubernetes": ["kubernetes", "k8s"],
    "MLflow": ["mlflow"],
    "DVC": ["dvc", "data version control"],
    "Airflow": ["airflow", "apache airflow"],
    "Prefect": ["prefect"],
    "FastAPI": ["fastapi"],
    "Flask": ["flask"],
    "REST API": ["rest api", "restful", "api development"],
    # Vector & Search
    "FAISS": ["faiss"],
    "Chroma": ["chromadb", "chroma"],
    "Pinecone": ["pinecone"],
    "Weaviate": ["weaviate"],
    "Elasticsearch": ["elasticsearch", "elastic search"],
    # Cloud
    "AWS": ["aws", "amazon web services", "s3", "ec2", "sagemaker"],
    "GCP": ["gcp", "google cloud", "vertex ai", "bigquery"],
    "Azure": ["azure", "microsoft azure", "azure ml"],
    # Data & Visualization
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Matplotlib": ["matplotlib"],
    "Seaborn": ["seaborn"],
    "Plotly": ["plotly"],
    "Spark": ["spark", "apache spark", "pyspark"],
    # General ML Concepts
    "Machine Learning": ["machine learning", "ml"],
    "Deep Learning": ["deep learning", "neural network", "cnn", "rnn", "lstm", "transformer"],
    "Computer Vision": ["computer vision", "cv", "image classification", "object detection", "yolo"],
    "Reinforcement Learning": ["reinforcement learning", "rl", "q-learning", "ppo"],
    "A/B Testing": ["a/b testing", "a/b test", "hypothesis testing", "experimentation"],
    "Feature Engineering": ["feature engineering", "feature selection", "feature extraction"],
    "Model Evaluation": ["model evaluation", "cross-validation", "confusion matrix", "roc", "auc", "f1"],
    "Git": ["git", "github", "gitlab", "version control"],
    "CI/CD": ["ci/cd", "cicd", "continuous integration", "github actions", "jenkins"],
}


def _compile_patterns() -> list[tuple[str, re.Pattern]]:
    compiled = []
    for skill_name, aliases in SKILL_TAXONOMY.items():
        parts = "|".join(aliases)
        pattern = re.compile(rf"(?<!\w)({parts})(?!\w)", re.IGNORECASE)
        compiled.append((skill_name, pattern))
    return compiled


_COMPILED_PATTERNS = _compile_patterns()


class SkillExtractor:
    """
    Extracts skills from text using:
    1. Rule-based matching against a curated AI/ML taxonomy
    2. Confidence scoring based on mention frequency
    """

    def extract(self, text: str) -> list[str]:
        """Return a deduplicated list of canonical skill names found in text."""
        found: dict[str, int] = {}
        text_lower = text.lower()

        for skill_name, pattern in _COMPILED_PATTERNS:
            matches = pattern.findall(text_lower)
            if matches:
                found[skill_name] = len(matches)

        # Sort by mention count (most mentioned first)
        return sorted(found.keys(), key=lambda s: found[s], reverse=True)

    def extract_with_scores(self, text: str) -> list[dict]:
        """Return skills with normalized confidence scores."""
        found: dict[str, int] = {}
        text_lower = text.lower()

        for skill_name, pattern in _COMPILED_PATTERNS:
            matches = pattern.findall(text_lower)
            if matches:
                found[skill_name] = len(matches)

        if not found:
            return []

        max_count = max(found.values())
        return [
            {
                "skill": skill,
                "mentions": count,
                "confidence": round(min(count / max_count, 1.0), 3),
            }
            for skill, count in sorted(found.items(), key=lambda x: x[1], reverse=True)
        ]

    def compute_overlap(
        self, resume_skills: list[str], jd_skills: list[str]
    ) -> dict:
        """Compute matching, missing, and extra skills."""
        resume_set = set(resume_skills)
        jd_set = set(jd_skills)

        matching = sorted(resume_set & jd_set)
        missing = sorted(jd_set - resume_set)
        extra = sorted(resume_set - jd_set)

        overlap_score = len(matching) / len(jd_set) if jd_set else 0.0

        return {
            "matching_skills": matching,
            "missing_skills": missing,
            "extra_skills": extra,
            "overlap_score": round(overlap_score, 4),
            "match_count": len(matching),
            "total_required": len(jd_set),
        }
