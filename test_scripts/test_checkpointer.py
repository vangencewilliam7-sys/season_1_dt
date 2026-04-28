import asyncio
import os
import sys
import uuid

sys.path.append(os.path.join(os.path.dirname(__file__), "knnowledge_Hub", "backend"))

from app.graph.pipeline import create_pipeline, global_checkpointer
from app.models.state import GraphState
from unittest.mock import Mock

async def test():
    print("Testing pipeline state retrieval...")
    
    # 1. Create a dummy thread ID
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    # 2. Get the pipeline
    pipeline = create_pipeline()
    
    # 3. Create a dummy state and save it manually
    state = GraphState(document_id=thread_id)
    # Wait, GraphState is a BaseModel. LangGraph get_state/update_state handles it.
    
    try:
        # LangGraph requires us to actually run the pipeline to save state, 
        # but we can try to update_state directly
        pipeline.update_state(config, state.dict() if hasattr(state, 'dict') else state)
        print("Successfully updated state in checkpointer.")
        
        # 4. Try to retrieve it
        retrieved = pipeline.get_state(config)
        print("Retrieved state:", retrieved)
        
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(test())
