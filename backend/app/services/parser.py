import os
from docx import Document
import fitz # PyMuPDF
from typing import List, Dict, Any
import uuid

class HierarchicalParser:
    @staticmethod
    def parse_docx(file_path: str) -> List[Dict[str, Any]]:
        doc = Document(file_path)
        chunks = []
        current_hierarchy = {1: None, 2: None, 3: None}
        
        for para in doc.paragraphs:
            if not para.text.strip():
                continue
                
            style = para.style.name.lower()
            level = 0
            if "heading 1" in style: level = 1
            elif "heading 2" in style: level = 2
            elif "heading 3" in style: level = 3
            
            chunk_id = str(uuid.uuid4())
            parent_id = None
            if level > 0:
                # Find parent at level-1
                if level > 1:
                    parent_id = current_hierarchy.get(level - 1)
                current_hierarchy[level] = chunk_id
                # Reset children levels
                for i in range(level + 1, 4):
                    current_hierarchy[i] = None
            else:
                # Leaf/Body paragraph - parent is the deepest head
                for i in range(3, 0, -1):
                    if current_hierarchy.get(i):
                        parent_id = current_hierarchy[i]
                        break
            
            chunks.append({
                "id": chunk_id,
                "content": para.text,
                "parent_id": parent_id,
                "level": level,
                "source_path": file_path,
                "metadata": {"style": style}
            })
        return chunks

    @staticmethod
    def parse_pdf(file_path: str) -> List[Dict[str, Any]]:
        doc = fitz.open(file_path)
        chunks = []
        # Basic implementation: treat each page or large block as a chunk
        # Advanced would detect font sizes for hierarchy
        for page_num, page in enumerate(doc):
            text = page.get_text()
            if not text.strip(): continue
            
            chunks.append({
                "id": str(uuid.uuid4()),
                "content": text,
                "parent_id": None, # Simple flat parsing for PDF MVP
                "level": 0,
                "source_path": file_path,
                "metadata": {"page": page_num + 1}
            })
        return chunks
