"""
runtime/services/embedding_service.py

Generates text embeddings using OpenAI's embedding API.

This is the same embedding model used by the Knowledge Hub to index
document_chunks and expert_dna records. Both systems MUST use the
same model + dimensionality for vector search to work.

Model: text-embedding-3-small (1536-dim)
"""

import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Generates 1536-dim embeddings for semantic search.

    Used by:
        - SupabaseReader (to search document_chunks)
        - retrieve_context_node (to search expert_dna at conversation time)
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-3-small"):
        self.model = model
        self._client = None

        if api_key:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=api_key)
                logger.info(f"[EmbeddingService] Initialised with model: {model}")
            except ImportError:
                logger.error("[EmbeddingService] openai package not installed. "
                             "Install with: pip install openai")
        else:
            logger.warning("[EmbeddingService] No OPENAI_API_KEY provided. "
                           "Embedding calls will return zero vectors.")

    def get_embedding(self, text: str) -> List[float]:
        """
        Generate a single embedding vector for the given text.

        Returns:
            List of 1536 floats. Returns a zero vector if no API key is set.
        """
        if not self._client:
            return [0.0] * 1536

        try:
            text = text.replace("\n", " ").strip()
            response = self._client.embeddings.create(
                input=[text],
                model=self.model,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"[EmbeddingService] Embedding generation failed: {e}")
            return [0.0] * 1536

    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.

        Returns:
            List of embedding vectors. Returns zero vectors on failure.
        """
        if not self._client:
            return [[0.0] * 1536] * len(texts)

        try:
            cleaned = [t.replace("\n", " ").strip() for t in texts]
            response = self._client.embeddings.create(
                input=cleaned,
                model=self.model,
            )
            return [d.embedding for d in response.data]
        except Exception as e:
            logger.error(f"[EmbeddingService] Batch embedding failed: {e}")
            return [[0.0] * 1536] * len(texts)
