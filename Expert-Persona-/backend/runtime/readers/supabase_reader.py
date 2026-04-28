"""
runtime/readers/supabase_reader.py

Concrete DocumentReader — reads from the Knowledge Hub's Supabase tables.

Data flow:
    Knowledge Hub uploads docs → Hierarchical Parser → document_chunks table
    This reader queries that table → returns Documents for extraction pipeline

Also reads from expert_dna (verified master cases) to provide the
extraction pipeline with pre-validated expert decision patterns.

This replaces the FilesystemReader when the Knowledge Hub is the data source.

Usage:
    reader = SupabaseReader(vault_service=vault)
    docs = reader.load("expert-uuid-123")
"""

import logging
from typing import List

from runtime.readers.base_reader import BaseDocumentReader, Document
from runtime.services.knowledge_vault import KnowledgeVaultService

logger = logging.getLogger(__name__)


class SupabaseReader(BaseDocumentReader):
    """
    Reads expert documents from the Knowledge Hub's Supabase tables.

    Two data sources:
        1. document_chunks — hierarchical parsed document content
        2. expert_dna — human-verified expert decisions (master cases)

    Both are combined into the Document list that the extraction pipeline consumes.
    """

    def __init__(self, vault_service: KnowledgeVaultService):
        """
        Args:
            vault_service: An initialised KnowledgeVaultService instance.
        """
        self.vault = vault_service

    def load(self, expert_id: str) -> List[Document]:
        """
        Load all documents for the given expert from the Knowledge Hub.

        Strategy:
            1. Try to load chunks by expert_id (requires expert_id column in KH)
            2. Fallback: load ALL chunks from ALL documents (for initial integration)
            3. Also load expert_dna records as master case documents

        Returns:
            Combined list of Documents from both document_chunks and expert_dna.
        """
        if not self.vault.is_connected:
            logger.warning("[SupabaseReader] Knowledge Vault not connected. "
                           "Returning empty document list.")
            return []

        documents = []

        # ── Source 1: Document Chunks (Knowledge Hub base knowledge) ───────
        chunks = self._load_document_chunks(expert_id)
        documents.extend(chunks)

        # ── Source 2: Expert DNA (verified master cases) ──────────────────
        dna_docs = self._load_expert_dna(expert_id)
        documents.extend(dna_docs)

        logger.info(f"[SupabaseReader] Total loaded: {len(documents)} documents "
                    f"({len(chunks)} chunks + {len(dna_docs)} DNA records) "
                    f"for expert: {expert_id}")
        return documents

    def _load_document_chunks(self, expert_id: str) -> List[Document]:
        """
        Load document chunks from the Knowledge Hub's document_chunks table.

        Tries expert_id first. If no results (expert_id column may not exist
        or not be populated yet), falls back to loading all available documents.
        """
        # Try by expert_id first
        chunks = self.vault.get_chunks_by_expert(expert_id)

        if not chunks:
            # Fallback: get all document IDs and load their chunks
            logger.info("[SupabaseReader] No chunks found by expert_id. "
                        "Falling back to all available documents.")
            doc_ids = self.vault.get_all_document_ids()

            if not doc_ids:
                logger.warning("[SupabaseReader] No documents found in Knowledge Hub.")
                return []

            chunks = []
            for doc_id in doc_ids:
                doc_chunks = self.vault.get_chunks_by_document(doc_id)
                chunks.extend(doc_chunks)

        # Convert to Document objects
        documents = []
        for chunk in chunks:
            # Reconstruct hierarchical context from parent chain
            content = chunk.get("content", "")
            if not content or not content.strip():
                continue

            documents.append(Document(
                source=f"supabase://document_chunks/{chunk.get('id', 'unknown')}",
                content=content.strip(),
                metadata={
                    "expert_id": expert_id,
                    "source_type": "knowledge_hub",
                    "document_id": chunk.get("document_id"),
                    "chunk_id": chunk.get("id"),
                    "parent_id": chunk.get("parent_id"),
                    "level": chunk.get("level", 0),
                    "source_path": chunk.get("source_path", ""),
                    "original_metadata": chunk.get("metadata", {}),
                },
            ))

        logger.info(f"[SupabaseReader] Loaded {len(documents)} document chunks.")
        return documents

    def _load_expert_dna(self, expert_id: str) -> List[Document]:
        """
        Load verified expert decisions from the expert_dna table.

        These are pre-validated master cases — the extraction pipeline can
        use them as reference heuristics / decision patterns.
        """
        # We don't know the expert's industry yet, so we load all DNA records.
        # The extraction pipeline's ingestion node will filter by relevance.
        # In the future, we can use expert_id on the expert_dna table directly.
        all_dna = []

        # Try to get DNA records — we load all industries for now
        for industry in ["fertility", "legal", "tech_consulting", "recruiting", "healthcare"]:
            records = self.vault.get_expert_dna_by_industry(industry)
            all_dna.extend(records)

        # Convert to Document objects
        documents = []
        for record in all_dna:
            decision = record.get("expert_decision", "")
            reasoning = record.get("reasoning", "")
            archetype = record.get("impact_archetype", "")

            # Format as a readable document for the extraction pipeline
            content = (
                f"VERIFIED EXPERT DECISION\n"
                f"========================\n"
                f"Decision: {decision}\n"
                f"Reasoning: {reasoning}\n"
                f"Impact Level: {archetype}\n"
                f"Industry: {record.get('industry', 'unknown')}\n"
                f"Scenario ID: {record.get('scenario_id', 'unknown')}"
            )

            documents.append(Document(
                source=f"supabase://expert_dna/{record.get('id', 'unknown')}",
                content=content,
                metadata={
                    "expert_id": expert_id,
                    "source_type": "master_cases",
                    "dna_id": record.get("id"),
                    "scenario_id": record.get("scenario_id"),
                    "impact_archetype": archetype,
                    "industry": record.get("industry"),
                },
            ))

        logger.info(f"[SupabaseReader] Loaded {len(documents)} expert DNA records.")
        return documents
