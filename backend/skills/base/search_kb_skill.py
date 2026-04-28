"""
skills/base/search_kb_skill.py

BaseSkill — Search Knowledge Base
SRP: One job — run a semantic search against the Knowledge Hub. No persona.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.interfaces.skill import BaseSkill, SkillParams, SkillResult


class SearchKBSkill(BaseSkill):
    """
    Raw capability: semantic search over the Knowledge Hub (Supabase/pgvector).
    Returns top-k chunks relevant to the query.

    Input params:
        query       : str   — The search query
        expert_id   : str   — Scope the search to a specific expert's KB
        top_k       : int   — Number of results to return (default: 5)
        min_score   : float — Minimum cosine similarity threshold (default: 0.6)
    """

    def __init__(self, vault_service=None, embedding_service=None):
        """
        DIP: inject vault and embedding services.
        Can be left None for testing (mock mode).
        """
        self._vault = vault_service
        self._embedder = embedding_service

    def get_skill_id(self) -> str:
        return "search_kb"

    def get_description(self) -> str:
        return "Semantic search over the expert's Knowledge Hub and Master Cases."

    def execute(self, params: SkillParams) -> SkillResult:
        try:
            p = params.raw_params
            query = p.get("query", "")
            expert_id = p.get("expert_id", "")
            top_k = p.get("top_k", 5)
            min_score = p.get("min_score", 0.6)

            if not query:
                return SkillResult(
                    success=False,
                    output=None,
                    skill_id=self.get_skill_id(),
                    error_message="Query string is required.",
                )

            if self._vault is None or self._embedder is None:
                # Mock mode for testing
                return SkillResult(
                    success=True,
                    output={"results": [], "mock": True, "query": query},
                    skill_id=self.get_skill_id(),
                    metadata={"mode": "mock"},
                )

            embedding = self._embedder.embed(query)
            results = self._vault.search(
                embedding=embedding,
                expert_id=expert_id,
                top_k=top_k,
                min_score=min_score,
            )

            return SkillResult(
                success=True,
                output={"results": results, "query": query, "top_k": top_k},
                skill_id=self.get_skill_id(),
                metadata={"expert_id": expert_id, "result_count": len(results)},
            )

        except Exception as e:
            return SkillResult(
                success=False,
                output=None,
                skill_id=self.get_skill_id(),
                error_message=str(e),
            )
