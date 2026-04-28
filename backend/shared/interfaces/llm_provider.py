"""
shared/interfaces/llm_provider.py

SOLID — Dependency Inversion
------------------------------
All nodes depend on BaseLLMProvider, never on a specific vendor.
Swap Groq → OpenAI → Ollama by changing one config line.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class LLMMessage:
    """Single message in a conversation."""
    role: str       # "system" | "user" | "assistant"
    content: str


@dataclass
class LLMResponse:
    """Standardized response from any LLM provider."""
    content: str
    model_id: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    finish_reason: Optional[str] = None     # "stop" | "length" | "error"


class BaseLLMProvider(ABC):
    """
    Abstract interface for any LLM provider.

    Concrete implementations:
      - GroqLLMProvider   → Groq API (Llama 3.x)
      - OpenAILLMProvider → OpenAI API (GPT-4o)
      - MockLLMProvider   → Deterministic test double
    """

    @abstractmethod
    def chat(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        """
        Send a chat-formatted prompt and return a response.

        Args:
            messages:    Ordered list of system/user/assistant messages.
            temperature: 0.0 = deterministic. 0.7 = balanced. 1.0 = creative.
            max_tokens:  Hard cap on output tokens. None = provider default.
            json_mode:   If True, force JSON-structured output (where supported).
        """

    @abstractmethod
    def get_model_id(self) -> str:
        """Return the model identifier string (e.g. 'llama-3.1-70b-versatile')."""
