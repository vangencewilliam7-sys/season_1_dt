"""
core/providers/base_llm.py

Abstract interface for LLM providers.
All LLM calls in the framework go through this interface.
Swap Groq → OpenAI → Ollama by changing ONE concrete class.

Rule: This file must never import from adapters/ or runtime/
"""

from abc import ABC, abstractmethod
from typing import List


class BaseLLMProvider(ABC):
    """
    Abstract LLM provider.
    Concrete implementations: providers/groq_llm.py, providers/ollama_llm.py
    """

    @abstractmethod
    def chat(
        self,
        messages: List[dict],
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> str:
        """
        Send a list of messages and return the assistant's response as a string.

        Args:
            messages: List of {"role": "system"|"user"|"assistant", "content": str}
            temperature: Sampling temperature (lower = more deterministic)
            max_tokens: Maximum response length

        Returns:
            The assistant's response text.
        """

    @abstractmethod
    def get_model_id(self) -> str:
        """Return the model identifier string for logging and tracing."""
