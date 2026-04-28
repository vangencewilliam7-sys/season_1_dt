"""
runtime/readers/base_reader.py

Abstract interface for reading from the existing Knowledge Hub + Master Cases.

This is the ONLY integration point between this framework and external data sources.
The framework never talks directly to any database, file system, or API —
it only calls reader.load() and receives Documents.

To connect to a new data source:
  1. Create runtime/readers/<source>_reader.py
  2. Subclass BaseDocumentReader
  3. Implement load()
  4. Run: pytest tests/test_reader_contract.py
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List


@dataclass
class Document:
    """
    A single unit of expert knowledge — one document from the KB or Master Cases.

    Attributes:
        source:   Where this came from (file path, URL, record ID, etc.)
        content:  The raw text content of the document
        metadata: Optional structured data (doc type, date, tags, etc.)
    """
    source: str
    content: str
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialise for LangGraph state (state values must be JSON-serialisable)."""
        return {
            "source": self.source,
            "content": self.content,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Document":
        """Deserialise from LangGraph state."""
        return cls(
            source=data.get("source", "unknown"),
            content=data.get("content", ""),
            metadata=data.get("metadata", {}),
        )


class BaseDocumentReader(ABC):
    """
    Abstract reader interface.

    The framework calls ONLY load(). All storage details are hidden behind
    this interface, making the extraction pipeline storage-agnostic.
    """

    @abstractmethod
    def load(self, expert_id: str) -> List[Document]:
        """
        Load all available documents for the given expert
        from the Knowledge Hub and Master Cases.

        Args:
            expert_id: The expert's unique identifier

        Returns:
            List of Document objects, each with source, content, and metadata.
            Returns an empty list if no documents are found (never raises).

        Notes:
            - This method performs NO embedding, NO chunking, NO storage.
            - Returns raw text documents only.
            - If the source KB requires filtering or transformation,
              do that here — the extraction pipeline shouldn't know about it.
        """
