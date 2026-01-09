# ==============================================================================
# FILE: src/main.py
# Main FastAPI application with routing for multiple AI apps
# ==============================================================================

import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Get the backend directory (parent of src)
backend_dir = Path(__file__).resolve().parent.parent
env_path = backend_dir / '.env'

# Load environment variables
load_dotenv(dotenv_path=env_path)

# Debug: Print to verify
print("=" * 60)
print("🚀 GenAI Multi-App Platform Starting...")
print("=" * 60)
print(f"🔍 Loading .env from: {env_path}")
print(f"📁 .env exists: {env_path.exists()}")

# Validate API key
API_KEY = os.getenv("GENAI_API_KEY")
if API_KEY:
    print(f"🔑 API Key loaded: Yes ✅")
    print(f"🔑 API Key (first 10 chars): {API_KEY[:10]}...")
else:
    print("❌ ERROR: GENAI_API_KEY not found!")
    print(f"Make sure .env file exists at: {env_path}")
    raise RuntimeError("GENAI_API_KEY not set in .env file")

print("=" * 60)

# Import routers AFTER loading env
from apps.search_engine.routes import router as search_router
from apps.knowledge_chatbot.routes import router as chatbot_router

# Lifespan event handler (replaces deprecated on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("\n✅ Server started successfully!")
    print("📚 API Documentation: http://localhost:8001/api/docs")
    print("🔍 Search Engine: http://localhost:8001/api/search")
    print("💬 Knowledge Chatbot: http://localhost:8001/api/chatbot")
    print("=" * 60 + "\n")
    yield
    # Shutdown
    print("\n👋 Server shutting down gracefully...")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="GenAI Multi-App Platform",
    description="Production-ready platform with Search Engine and Knowledge Chatbot",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "GenAI Multi-App Platform API",
        "version": "1.0.0",
        "status": "online",
        "apps": {
            "search_engine": "/api/search",
            "knowledge_chatbot": "/api/chatbot"
        },
        "documentation": "/api/docs"
    }

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "search_engine": "operational",
            "knowledge_chatbot": "operational"
        },
        "gemini_api": "connected"
    }

# Register app routers with prefixes
app.include_router(
    search_router,
    prefix="/api/search",
    tags=["Search Engine"]
)

app.include_router(
    chatbot_router,
    prefix="/api/chatbot",
    tags=["Knowledge Chatbot"]
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",  # Import string format for reload
        host="0.0.0.0", 
        port=8001, 
        reload=True,
        log_level="info"
    )