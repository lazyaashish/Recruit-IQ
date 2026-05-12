"""
Provider-agnostic LLM abstraction layer.
Supports OpenAI-compatible APIs (OpenAI, Anthropic via proxy, local Ollama, etc.)
Falls back gracefully to deterministic output when no provider is configured.
"""
from __future__ import annotations

from typing import Optional

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class LLMService:
    """
    Thin wrapper around LLM providers.
    When no provider is configured, all methods return None and callers
    must use deterministic fallbacks.
    """

    def __init__(self):
        self._client = None
        self._provider = settings.llm_provider
        self._model = settings.llm_model
        if self._provider:
            self._init_client()

    def _init_client(self):
        try:
            if self._provider == "openai":
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=settings.llm_api_key,
                    base_url=settings.llm_base_url,
                )
                logger.info("LLM client initialized", provider="openai")
            elif self._provider == "anthropic":
                import anthropic
                self._client = anthropic.Anthropic(api_key=settings.llm_api_key)
                logger.info("LLM client initialized", provider="anthropic")
            else:
                logger.warning("Unknown LLM provider, running without LLM", provider=self._provider)
        except ImportError as e:
            logger.warning("LLM SDK not installed", error=str(e))

    @property
    def available(self) -> bool:
        return self._client is not None

    def complete(
        self,
        prompt: str,
        system: str = "You are a helpful AI career coach.",
        max_tokens: int = 800,
        temperature: float = 0.3,
    ) -> Optional[str]:
        """
        Run a completion. Returns None if LLM is unavailable.
        Callers MUST handle None with a deterministic fallback.
        """
        if not self.available:
            return None

        try:
            if self._provider == "openai":
                response = self._client.chat.completions.create(
                    model=self._model or "gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                return response.choices[0].message.content

            elif self._provider == "anthropic":
                response = self._client.messages.create(
                    model=self._model or "claude-haiku-4-5-20251001",
                    max_tokens=max_tokens,
                    system=system,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.content[0].text

        except Exception as e:
            logger.error("LLM completion failed", error=str(e))
            return None

    def enrich_suggestions(self, context: dict) -> Optional[list[str]]:
        """
        Use LLM to generate richer improvement suggestions.
        Falls back to deterministic output if unavailable.
        """
        if not self.available:
            return None

        prompt = (
            f"A candidate is applying for: {context.get('role', 'an AI/ML role')}.\n"
            f"Their resume match score is {context.get('score', 0):.0%}.\n"
            f"Missing skills: {', '.join(context.get('missing_skills', [])[:8])}.\n"
            f"Top keyword gaps: {', '.join(context.get('keyword_gaps', [])[:5])}.\n\n"
            "Give 3 concise, actionable suggestions to improve their resume for this role. "
            "Each suggestion should be one sentence and start with an action verb."
        )
        result = self.complete(prompt, max_tokens=400)
        if result:
            lines = [l.strip().lstrip("•-123456789. ") for l in result.split("\n") if l.strip()]
            return lines[:5]
        return None

    def enrich_roadmap_summary(self, missing_skills: list[str], role: str) -> Optional[str]:
        """Generate a short narrative intro for the roadmap."""
        if not self.available or not missing_skills:
            return None

        prompt = (
            f"A candidate targeting the role of '{role}' is missing these skills: "
            f"{', '.join(missing_skills[:10])}.\n"
            "Write a 2-sentence motivational overview of their learning roadmap. "
            "Be direct, practical, and encouraging."
        )
        return self.complete(prompt, max_tokens=150)
