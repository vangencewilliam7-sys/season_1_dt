"""
runtime/readers/sql_reader.py

Concrete DocumentReader — reads from a SQL database (Postgres/MySQL/etc.).

Use when:
- Knowledge Hub is stored in relational tables
- Master Cases are records in a 'cases' table
"""

import logging
from typing import List
import psycopg2  # Standard for Postgres, can be swapped for SQLAlchemy
from runtime.readers.base_reader import BaseDocumentReader, Document

logger = logging.getLogger(__name__)


class SQLReader(BaseDocumentReader):
    """
    Reads expert documents from a SQL database.
    Assumes a standard (source, content, metadata) schema.
    """

    def __init__(self, connection_string: str, table_name: str = "expert_documents"):
        """
        Args:
            connection_string: DSN or URL for the database.
            table_name: The table containing the expert data.
        """
        self.connection_string = connection_string
        self.table_name = table_name

    def load(self, expert_id: str) -> List[Document]:
        """
        Query the DB for all records matching the expert_id.
        """
        logger.info(f"[SQLReader] Querying {self.table_name} for expert: {expert_id}")
        
        documents = []
        conn = None
        try:
            conn = psycopg2.connect(self.connection_string)
            cur = conn.cursor()
            
            # Adjust query based on actual schema once confirmed by user
            query = f"SELECT source_id, body, metadata FROM {self.table_name} WHERE expert_id = %s"
            cur.execute(query, (expert_id,))
            
            rows = cur.fetchall()
            for row in rows:
                documents.append(Document(
                    source=f"db://{row[0]}",
                    content=row[1],
                    metadata=row[2] if isinstance(row[2], dict) else {}
                ))
                
            cur.close()
            logger.info(f"[SQLReader] Successfully loaded {len(documents)} records from DB.")
            
        except Exception as e:
            logger.error(f"[SQLReader] Database query failed: {e}")
        finally:
            if conn:
                conn.close()
                
        return documents
