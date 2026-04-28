"""
shared/interfaces/document_reader.py

SOLID — Interface Segregation + Dependency Inversion
------------------------------------------------------
This is the ONE integration contract between the Knowledge Hub and the
Expert Persona. Neither system imports the other directly.

Any new storage backend (S3, MongoDB, another API) = one new concrete class.
Zero changes to the consumers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Document:
    """
    A single unit of expert knowledge, as returned by any reader.
    Source-agnostic — consumers never need to know where this came from.
    """
    source: str                    # File path, URL, Supabase record ID, etc.
    content: str                   # Raw text content
    metadata: dict = field(default_factory=dict)  # Level, type, tags, parent path

    # Hierarchy fields (populated for Knowledge Hub chunks)
    heading_level: Optional[int] = None   # 1=H1, 2=H2, 3=H3, None=body
    parent_id: Optional[str] = None       # Parent chunk UUID
    section_path: Optional[str] = None    # "H1 > H2 > H3" breadcrumb

    # Master Case flag (populated when the document is an expert decision)
    is_master_case: bool = False


class BaseDocumentReader(ABC):
    """
    Abstract interface to any knowledge source.

    IMPLEMENT THIS to connect the Expert Persona framework to any storage:
      - FilesystemReader  → reads local files
      - SupabaseReader    → reads the live Knowledge Hub DB
      - APIReader         → reads from an HTTP endpoint
      - SQLReader         → reads from any SQL database

    The Expert Persona framework ONLY calls load(). It never calls
    any database, file system, or API directly.
    """

    @abstractmethod
    def load(self, expert_id: str) -> List[Document]:
        """
        Load all available knowledge for this expert.

        Returns a flat list of Document objects — both raw chunks
        (from the hierarchical structure) and Master Cases.
        The caller does not distinguish — it just reads the list.

        Args:
            expert_id: UUID string identifying the expert.

        Returns:
            List[Document] sorted by hierarchy (H1 first, body last).
        """

    @abstractmethod
    def health_check(self) -> bool:
        """Return True if the underlying source is reachable."""
