from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import ingest, query

app = FastAPI(title="Knowledge Hub - Standalone Brain Factory")

# Configure CORS for local standalone development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Modular Routers
app.include_router(ingest.router, prefix="/api", tags=["Ingestion"])
app.include_router(query.router, prefix="/api", tags=["Query"])

@app.get("/")
async def root():
    return {
        "message": "Knowledge Hub API is running",
        "version": "1.0.0",
        "architecture": "Standalone Brain Factory"
    }
