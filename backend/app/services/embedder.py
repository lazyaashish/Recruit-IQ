"""
Embedding service using sentence-transformers.
Provides semantic similarity scoring between resume and job description.
Falls back to TF-IDF cosine similarity if sentence-transformers is unavailable.
"""
from __future__ import annotations

import hashlib
import pickle
from pathlib import Path
from typing import Optional

import numpy as np
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class EmbeddingService:
    """
    Wraps sentence-transformers for semantic text embeddings.
    Singleton pattern with lazy loading.
    """

    _instance: Optional["EmbeddingService"] = None
    _model = None
    _use_transformers: bool = True

    def __new__(cls) -> "EmbeddingService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _load_model(self):
        if self._model is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(
                settings.embedding_model, device=settings.embedding_device
            )
            self._use_transformers = True
            logger.info("Loaded sentence-transformer model", model=settings.embedding_model)
        except Exception as e:
            logger.warning("sentence-transformers unavailable, using TF-IDF fallback", error=str(e))
            self._use_transformers = False
            self._init_tfidf_fallback()

    def _init_tfidf_fallback(self):
        """TF-IDF based fallback embedder."""
        from sklearn.feature_extraction.text import TfidfVectorizer
        self._tfidf = TfidfVectorizer(max_features=5000, stop_words="english")
        self._tfidf_fitted = False

    def encode(self, texts: list[str]) -> np.ndarray:
        """Encode a list of texts into embedding vectors."""
        self._load_model()
        if self._use_transformers:
            return self._model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        else:
            return self._encode_tfidf(texts)

    def _encode_tfidf(self, texts: list[str]) -> np.ndarray:
        from sklearn.preprocessing import normalize
        if not self._tfidf_fitted:
            matrix = self._tfidf.fit_transform(texts)
            self._tfidf_fitted = True
        else:
            matrix = self._tfidf.transform(texts)
        dense = matrix.toarray()
        return normalize(dense)

    def semantic_similarity(self, text_a: str, text_b: str) -> float:
        """
        Compute cosine similarity between two texts.
        Returns a float in [0, 1].
        """
        self._load_model()
        if self._use_transformers:
            vecs = self.encode([text_a, text_b])
            # Vectors are already normalized
            sim = float(np.dot(vecs[0], vecs[1]))
        else:
            # Re-fit with both texts for TF-IDF
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            vec = TfidfVectorizer(stop_words="english")
            matrix = vec.fit_transform([text_a, text_b])
            sim = float(cosine_similarity(matrix[0], matrix[1])[0][0])

        # Clamp to [0, 1]
        return max(0.0, min(1.0, sim))

    def batch_similarity(self, query: str, candidates: list[str]) -> list[float]:
        """Compute similarity from query to each candidate."""
        self._load_model()
        all_texts = [query] + candidates
        if self._use_transformers:
            vecs = self.encode(all_texts)
            query_vec = vecs[0]
            scores = [float(np.dot(query_vec, vecs[i + 1])) for i in range(len(candidates))]
        else:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            vec = TfidfVectorizer(stop_words="english")
            matrix = vec.fit_transform(all_texts)
            sims = cosine_similarity(matrix[0:1], matrix[1:])
            scores = sims[0].tolist()
        return [max(0.0, min(1.0, s)) for s in scores]


def get_text_fingerprint(text: str) -> str:
    """Stable hash for caching embeddings."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]
