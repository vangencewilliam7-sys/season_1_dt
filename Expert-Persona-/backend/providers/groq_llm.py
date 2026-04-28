"""
providers/groq_llm.py

Concrete LLM provider — Groq API (Llama 3.1 models)

Used for both extraction nodes:
- Ingestion node: groq_ingestion_model (larger/more capable)
- Journalist node: groq_journalist_model (smaller/faster)

Swap to OpenAI or Ollama by implementing BaseLLMProvider instead.
"""

import logging
from typing import List

from groq import Groq

from core.providers.base_llm import BaseLLMProvider

logger = logging.getLogger(__name__)


class GroqLLMProvider(BaseLLMProvider):
    """
    Concrete LLM provider using the Groq API.
    Wraps the Groq client to match the BaseLLMProvider interface.
    """

    def __init__(self, api_key: str, model_id: str):
        """
        Args:
            api_key: Groq API key (from settings)
            model_id: Model to use, e.g. "llama-3.1-70b-versatile"
        """
        self._model_id = model_id
        self._client = Groq(api_key=api_key)
        logger.info(f"[GroqLLM] Initialised with model: {model_id}")

    def chat(
        self,
        messages: List[dict],
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> str:
        """
        Send messages to Groq and return the response text.

        Raises:
            Exception: If the Groq API call fails (let it propagate to the node)
        """
        logger.debug(f"[GroqLLM] Sending {len(messages)} messages to {self._model_id}")

        completion = self._client.chat.completions.create(
            model=self._model_id,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        response_text = completion.choices[0].message.content
        logger.debug(f"[GroqLLM] Received {len(response_text)} characters")

        return response_text

    def get_model_id(self) -> str:
        return self._model_id
