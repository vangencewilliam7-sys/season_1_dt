"""
runtime/readers/api_reader.py

Concrete DocumentReader — reads from a REST API endpoint.

Use when:
- Knowledge Hub is exposed via a service
- Master Cases are managed in a central portal
- Real-time fetching of expert documents is required

Expected JSON format from the API:
{
    "expert_id": "...",
    "documents": [
        {
            "id": "doc_001",
            "title": "...",
            "body": "...",
            "type": "hub" | "case",
            "updated_at": "..."
        },
        ...
    ]
}
"""

import logging
from typing import List, Optional
import httpx

from runtime.readers.base_reader import BaseDocumentReader, Document

logger = logging.getLogger(__name__)


class APIReader(BaseDocumentReader):
    """
    Reads expert documents from a external JSON API.
    """

    def __init__(
        self,
        base_url: str,
        token: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Args:
            base_url: The endpoint to query for expert data.
            token: Bearer token for authentication.
            timeout: Request timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}
        self.timeout = timeout

    def load(self, expert_id: str) -> List[Document]:
        """
        Fetch documents for the expert from the API.
        """
        url = f"{self.base_url}/experts/{expert_id}/documents"
        
        logger.info(f"[APIReader] Fetching documents from {url}")

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()

            docs_raw = data.get("documents", [])
            documents = []

            for d in docs_raw:
                documents.append(Document(
                    source=f"api://{d.get('id', 'unknown')}",
                    content=d.get("body", d.get("content", "")),
                    metadata={
                        "title": d.get("title"),
                        "type": d.get("type"),
                        "api_id": d.get("id"),
                        "updated_at": d.get("updated_at")
                    }
                ))

            logger.info(f"[APIReader] Successfully fetched {len(documents)} documents.")
            return documents

        except httpx.HTTPError as e:
            logger.error(f"[APIReader] HTTP request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"[APIReader] Unexpected error during API fetch: {e}")
            return []
