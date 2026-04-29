from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .api import ingest, query, chat
import os

app = FastAPI(title="Knowledge Hub - Standalone Brain Factory")

# Configure CORS for local standalone development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"], # Allow Vite and Next.js default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Modular Routers
app.include_router(ingest.router, prefix="/api", tags=["Ingestion"])
app.include_router(query.router, prefix="/api", tags=["Query"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])

# Mount uploads directory for static file serving (document viewer)
uploads_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "uploads"))
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

@app.get("/")
async def root():
    return {
        "message": "Knowledge Hub API is running",
        "version": "1.0.0",
        "architecture": "Standalone Brain Factory"
    }
