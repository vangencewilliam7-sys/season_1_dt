from ...models.state import GraphState
from ...services.parser import HierarchicalParser
from ...services.embeddings import EmbeddingService
from ...services.supabase_client import SupabaseService
from ...models.schemas import DocumentChunk
import os

def ingestion_node(state: GraphState) -> GraphState:
    print(f"--- INGESTION: Processing Document {state.document_id} ---")
    
    # Ideally the state would carry the file path. For MVP, we search the uploads folder.
    # We'll assume for now there's a convention or we add it to state.
    # Let's assume we use the first doc in docs/ for now to test or a specific path.
    
    # In a real flow, the API would have passed the path in the state.
    # Since I just updated state.py, I'll assume we can use state.document_id to find the file.
    
    # For demo purposes, if no chunks are provided, we look at the docs folder
    docs_dir = r'd:\knnowledge_Hub\docs'
    parser = HierarchicalParser()
    embedder = EmbeddingService()
    db = SupabaseService()
    
    all_chunks = []
    
    # Process all docs in the docs folder for the initial "Knowledge Ingestion"
    for fname in os.listdir(docs_dir):
        if fname.endswith('.docx') or fname.endswith('.pdf'):
            path = os.path.join(docs_dir, fname)
            if fname.endswith('.docx'):
                chunks = parser.parse_docx(path)
            else:
                chunks = parser.parse_pdf(path)
            
            # Generate embeddings and prepare for DB
            texts = [c["content"] for c in chunks]
            embeddings = embedder.get_embeddings_batch(texts)
            
            db_chunks = []
            for i, chunk in enumerate(chunks):
                chunk["embedding"] = embeddings[i]
                chunk["document_id"] = state.document_id
                db_chunks.append(chunk)
                # Also update state
                all_chunks.append(DocumentChunk(**chunk))
            
            # Save to Supabase
            db.insert_chunks(db_chunks)
            print(f"Ingested {len(chunks)} chunks from {fname}")

    state.raw_chunks = all_chunks
    return state
