import re
from typing import List
import os
from .context_manager import ContextManager
from ..models.schemas import DecisionGap

class DivergenceScanner:
    def __init__(self, industry: str = "fertility"):
        self.context_manager = ContextManager(industry=industry)
        ctx = self.context_manager.get_context()
        # Semantic markers loaded from industry-specific context pack
        self.markers = ctx["semantic_markers"]

    def scan_text(self, text: str, chunk_id: str) -> List[DecisionGap]:
        gaps = []
        # 1. Regex based fast scanning for industry-specific markers
        for marker in self.markers:
            if re.search(marker, text, re.IGNORECASE):
                gaps.append(DecisionGap(
                    id=f"gap-{os.urandom(4).hex()}",
                    gap_type="Semantic Marker",
                    ambiguous_text=text,
                    source_chunk_id=chunk_id
                ))
                break # One primary gap per chunk to maintain focus
        
        return gaps
