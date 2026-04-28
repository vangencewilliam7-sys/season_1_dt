"""
runtime/services/knowledge_vault.py

Client for the Knowledge Hub's Supabase-backed Logic Vault.

This service wraps all read operations against the Knowledge Hub's tables:
    - document_chunks   — raw ingested knowledge (for extraction pipeline)
    - expert_dna        — human-verified expert decisions (for conversation runtime)

It uses the same Supabase RPC functions that the Knowledge Hub itself uses:
    - match_chunks(query_embedding, match_threshold, match_count)
    - match_expert_dna(query_embedding, match_threshold, match_count)

CRITICAL: This service is READ-ONLY. The Knowledge Hub is the sole writer.
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class KnowledgeVaultService:
    """
    Read-only client for the Knowledge Hub's Supabase tables.

    Used by:
        - SupabaseReader.load() → fetch document_chunks for extraction
        - retrieve_context_node() → search expert_dna for conversation
    """

    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        self._client = None

        if supabase_url and supabase_key:
            try:
                from supabase import create_client
                self._client = create_client(supabase_url, supabase_key)
                logger.info("[KnowledgeVault] Connected to Supabase Logic Vault.")
            except ImportError:
                logger.error("[KnowledgeVault] supabase package not installed. "
                             "Install with: pip install supabase")
            except Exception as e:
                logger.error(f"[KnowledgeVault] Failed to connect to Supabase: {e}")
        else:
            logger.warning("[KnowledgeVault] No Supabase credentials provided. "
                           "Knowledge Hub integration is disabled.")

    @property
    def is_connected(self) -> bool:
        """Check if the Supabase client is available."""
        return self._client is not None

    # ──────────────────────────────────────────────────────────────────────────
    # DOCUMENT CHUNKS — For the extraction pipeline (SupabaseReader)
    # ──────────────────────────────────────────────────────────────────────────

    def get_chunks_by_expert(self, expert_id: str) -> List[Dict[str, Any]]:
        """
        Fetch all document chunks belonging to a specific expert.

        Returns:
            List of chunk dicts with: id, content, parent_id, level,
            source_path, metadata, document_id.
        """
        if not self._client:
            return []

        try:
            response = (
                self._client
                .table("document_chunks")
                .select("id, content, parent_id, level, source_path, metadata, document_id")
                .eq("expert_id", expert_id)
                .order("created_at")
                .execute()
            )
            logger.info(f"[KnowledgeVault] Fetched {len(response.data)} chunks "
                        f"for expert: {expert_id}")
            return response.data
        except Exception as e:
            logger.error(f"[KnowledgeVault] Failed to fetch chunks: {e}")
            return []

    def get_chunks_by_document(self, document_id: str) -> List[Dict[str, Any]]:
        """
        Fetch all chunks for a specific document_id.
        Fallback when expert_id mapping is not yet set up.
        """
        if not self._client:
            return []

        try:
            response = (
                self._client
                .table("document_chunks")
                .select("id, content, parent_id, level, source_path, metadata, document_id")
                .eq("document_id", document_id)
                .order("created_at")
                .execute()
            )
            logger.info(f"[KnowledgeVault] Fetched {len(response.data)} chunks "
                        f"for document: {document_id}")
            return response.data
        except Exception as e:
            logger.error(f"[KnowledgeVault] Failed to fetch chunks by document: {e}")
            return []

    def get_all_document_ids(self) -> List[str]:
        """
        List all distinct document_ids in the document_chunks table.
        Useful for discovery when expert_id mapping is not set.
        """
        if not self._client:
            return []

        try:
            response = (
                self._client
                .table("document_chunks")
                .select("document_id")
                .execute()
            )
            return list({row["document_id"] for row in response.data})
        except Exception as e:
            logger.error(f"[KnowledgeVault] Failed to list document IDs: {e}")
            return []

    # ──────────────────────────────────────────────────────────────────────────
    # EXPERT DNA — For the conversation runtime (retrieve_context_node)
    # ──────────────────────────────────────────────────────────────────────────

    def search_expert_dna(
        self,
        query_embedding: List[float],
        threshold: float = 0.70,
        limit: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Semantic search over the high-purity Expert DNA Vault.

        This calls the Knowledge Hub's `match_expert_dna` RPC function — the
        same function used by the KH's own query endpoint and tools.py.

        Args:
            query_embedding: 1536-dim vector for the user's query.
            threshold: Minimum cosine similarity (default 0.70).
            limit: Maximum results to return.

        Returns:
            List of dicts with: id, scenario_id, expert_decision,
            impact_archetype, industry, reasoning, similarity.
        """
        if not self._client:
            return []

        try:
            response = self._client.rpc("match_expert_dna", {
                "query_embedding": query_embedding,
                "match_threshold": threshold,
                "match_count": limit,
            }).execute()

            logger.info(f"[KnowledgeVault] Expert DNA search returned "
                        f"{len(response.data)} results (threshold={threshold})")
            return response.data
        except Exception as e:
            logger.error(f"[KnowledgeVault] Expert DNA search failed: {e}")
            return []

    def search_raw_chunks(
        self,
        query_embedding: List[float],
        threshold: float = 0.50,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Semantic search over raw document_chunks (unverified knowledge).

        Use for exploratory context ONLY — never for production answers.
        Production answers come exclusively from search_expert_dna().

        Calls the Knowledge Hub's `match_chunks` RPC function.
        """
        if not self._client:
            return []

        try:
            response = self._client.rpc("match_chunks", {
                "query_embedding": query_embedding,
                "match_threshold": threshold,
                "match_count": limit,
            }).execute()

            logger.info(f"[KnowledgeVault] Raw chunk search returned "
                        f"{len(response.data)} results")
            return response.data
        except Exception as e:
            logger.error(f"[KnowledgeVault] Raw chunk search failed: {e}")
            return []

    # ──────────────────────────────────────────────────────────────────────────
    # MASTER CASES — For enriched extraction input
    # ──────────────────────────────────────────────────────────────────────────

    def get_expert_dna_by_industry(self, industry: str) -> List[Dict[str, Any]]:
        """
        Fetch all verified expert decisions for a given industry/domain.

        Used by SupabaseReader to provide master case context to the
        extraction pipeline.
        """
        if not self._client:
            return []

        try:
            response = (
                self._client
                .table("expert_dna")
                .select("id, scenario_id, expert_decision, impact_archetype, "
                        "industry, reasoning")
                .eq("industry", industry)
                .execute()
            )
            logger.info(f"[KnowledgeVault] Fetched {len(response.data)} DNA records "
                        f"for industry: {industry}")
            return response.data
        except Exception as e:
            logger.error(f"[KnowledgeVault] Failed to fetch DNA by industry: {e}")
            return []
